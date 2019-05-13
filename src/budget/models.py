# coding=utf-8
# Copyright (c) 2018 Janusz Skonieczny

import logging
from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q, Sum, signals
from django.dispatch import receiver
from django.shortcuts import resolve_url
from django.utils.translation import ugettext_lazy as _
from django_powerbank.db.models.base import BaseModel
from django_powerbank.db.models.fields import ChoicesIntEnum

from website.misc.mail import send_mail_template

log = logging.getLogger(__name__)


class AccountGroup(BaseModel):
    name = models.CharField(_('name'), max_length=255)
    number = models.PositiveSmallIntegerField(_('number'), default=0, unique=True)
    description = models.CharField(_('description'), max_length=255)

    class Meta:
        verbose_name = _('account group')
        verbose_name_plural = _('account groups')
        ordering = 'number', 'name',

    def __str__(self):
        return '{} {}'.format(self.number, self.name)

    def get_absolute_url(self):
        return resolve_url("budget:AccountGroupDetail", self.pk)


class Account(BaseModel):
    name = models.CharField(_('name'), max_length=255)
    group = models.ForeignKey(AccountGroup, on_delete=models.CASCADE, null=True, blank=True)
    group_no = models.PositiveSmallIntegerField(_('group'), default=0)
    number = models.PositiveSmallIntegerField(_('number'), default=0)
    description = models.CharField(_('description'), max_length=255)

    class Meta:
        verbose_name = _('account')
        verbose_name_plural = _('accounts')
        ordering = 'group_no', 'number', 'name',

    def __str__(self):
        return '{}-{:02} {}'.format(self.group.number, self.number, self.name)

    def get_absolute_url(self):
        return resolve_url("budget:AccountDetail", self.pk)


class Budget(BaseModel):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.DecimalField(_('amount'), default=0, decimal_places=0, max_digits=6)
    spent = models.DecimalField(_('money spent'), default=0, decimal_places=0, max_digits=6)
    available = models.DecimalField(_('money available'), default=0, decimal_places=0, max_digits=6)
    year = models.PositiveSmallIntegerField(_('year'), validators=[MaxValueValidator(2100), MinValueValidator(2019)])
    month = models.PositiveSmallIntegerField(_('month'), validators=[MaxValueValidator(12), MinValueValidator(1)])

    class Meta:
        verbose_name = _('budget')
        verbose_name_plural = _('budgets')
        ordering = 'year', 'month',
        unique_together = ('year', 'month', 'account')

    def __str__(self):
        return '{}-{:02} {}'.format(self.year, self.month, self.account.name)

    def get_absolute_url(self):
        return resolve_url("budget:BudgetDetail", self.pk)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.available = self.amount - self.spent
        super().save(force_insert, force_update, using, update_fields)

    def update_available(self):
        spent = Application.objects.filter(budget=self, approval=True).aggregate(Sum('amount'))['amount__sum']
        self.spent = spent or 0
        self.save()


class Application(BaseModel):
    date = models.DateField(_('date'), help_text=_('Approximate payment due date'))
    amount = models.DecimalField(_('amount'), decimal_places=0, max_digits=6, help_text=_('What is the total cost?'))
    title = models.CharField(_('title'), max_length=150, help_text=_('Short distinguishing name for this expenditure'))
    description = models.TextField(_('description'), help_text=_('Please describe and justify this expenditure.'))
    requester = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    manager = models.ForeignKey(
        get_user_model(), on_delete=models.PROTECT, null=True, blank=True,
        related_name='+', limit_choices_to=Q(groups__name='Managers')
    )
    submitted = models.DateField(_('submission date'), null=True, blank=True)
    # accountant = models.ForeignKey(
    #     get_user_model(), on_delete=models.PROTECT, null=True, blank=True,
    #     related_name='+', limit_choices_to=Q(groups__name='Accountants')
    # )
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, null=True, blank=True,
        help_text=_('Please select a budget that need to be decreased'))
    budget = models.ForeignKey(
        Budget, on_delete=models.CASCADE, null=True, blank=True,
        help_text=_('Please select a budget that need to be decreased'))
    # control = models.ForeignKey(
    #     get_user_model(), on_delete=models.PROTECT, null=True, blank=True,
    #     related_name='+', limit_choices_to=Q(groups__name='Controllers')
    # )
    approval = models.NullBooleanField(_('approval'))

    class Meta:
        verbose_name = _('expenditure request')
        verbose_name_plural = _('expenditure requests')
        ordering = '-date', 'amount',

    def __str__(self):
        return '{:%Y-%m-%d %H:%M}-{} {:03}'.format(self.date, self.requester, self.amount)

    def get_absolute_url(self):
        return resolve_url("budget:ApplicationDetail", self.pk)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.account:
            budget = Budget.objects.filter(year=self.date.year, month=self.date.month, account=self.account).first()
            if not budget:
                amount = Budget.objects.filter(account=self.account).first().amount
                budget, x = Budget.objects.get_or_create(
                    year=self.date.year,
                    month=self.date.month,
                    account=self.account,
                    defaults={'amount': amount}
                )
            self.budget = budget

        super().save(force_insert, force_update, using, update_fields)

    def get_decision(self, kind):
        return self.decisions.filter(kind=kind).first()

    @property
    def amount_available(self):
        if self.approval is True:
            return self.budget.available
        return self.budget.available - self.amount

    def send_notifications(self):
        log.debug("self.approval: %s", self.approval)
        if self.approval is not None:
            subject = _("{status}: {title}")
            template = "Application/email/approval_result.html"
            self.send_notification(self.requester, subject, template)
            return

        decisions = sorted((i.value for i in DecisionKind))
        first, decisions = decisions[0], decisions[1:]

        if not self.get_decision(first):
            self.send_approval_request(self.manager)
            return

        for kind in decisions:
            if not self.get_decision(kind):
                self.send_to_group(kind)
                break

    def send_to_group(self, kind):

        DECISION_GROUPS = {
            DecisionKind.accountant: settings.BUDGET_ACCOUNTANTS_GROUP,
            DecisionKind.control: settings.BUDGET_MANAGERS_GROUP,
            DecisionKind.manager: settings.BUDGET_CONTROL_GROUP,
        }

        group = DECISION_GROUPS[kind]
        log.debug("To group: %s", group)
        group, x = Group.objects.get_or_create(name=group)
        users = group.user_set.all()
        for user in users:
            self.send_approval_request(user)

    def send_approval_request(self, user):
        subject = _("{title} - expenditure for {amount} requires approval")
        template = "Application/email/approve_request.html"
        self.send_notification(user, subject, template)

    def send_notification(self, user, subject, template):
        log.debug("Sending to: %s", user)
        assert user.email, "User {} does not have an email set".format(user)
        url = resolve_url("budget:ApplicationDetail", self.pk)
        url = '{base_url}{url}'.format(base_url=settings.BASE_URL, url=url)
        ctx = {
            'title': self.title,
            'status': _('Approved') if self.approval else _('Rejected'),
            'amount': self.amount,
            'person': user,
            'object': self,
            'url': url,
        }
        subject = subject.format(**ctx)
        send_mail_template(template, ctx, subject, to=user.email)


class DecisionKind(ChoicesIntEnum):
    manager = 100
    accountant = 200,
    control = 1000,


class Decision(BaseModel):
    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    request = models.ForeignKey(Application, on_delete=models.CASCADE)
    ts = models.DateTimeField(_('time stamp'), default=datetime.now)
    kind = models.PositiveSmallIntegerField(_('approval step'), choices=DecisionKind.choices())
    approval = models.NullBooleanField(_('approval'))
    notes = models.TextField(_('notes'), null=True, blank=True)

    class Meta:
        verbose_name = _('decision')
        verbose_name_plural = _('decisions')
        default_related_name = 'decisions'
        unique_together = ('request', 'kind')

    def __str__(self):
        return '{} ({}): {}'.format(self.user, self.kind, self.approval)


# noinspection PyUnusedLocal
@receiver(signals.post_save, sender=get_user_model())
def team_membership(sender, instance=None, **kwargs):
    if settings.BUDGET_TEAM_DOMAIN in instance.email:
        from django.contrib.auth.models import Group
        team, new = Group.objects.get_or_create(name='Team')
        team.user_set.add(instance)


# noinspection PyUnusedLocal
@receiver(signals.post_save, sender=Application)
def budget_update(sender, instance=None, **kwargs):
    instance.send_notifications()
    if instance.budget_id is None:
        return

    instance.budget.update_available()
