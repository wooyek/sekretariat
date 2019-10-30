# coding=utf-8
# Copyright (c) 2018 Janusz Skonieczny

import logging
from collections import OrderedDict
from datetime import datetime
from functools import reduce

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q, Sum, signals
from django.dispatch import receiver
from django.shortcuts import resolve_url
from django.utils.functional import SimpleLazyObject, cached_property
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

    @property
    def full_no(self):
        return '{}-{:02}'.format(self.group.number, self.number)

    def get_absolute_url(self):
        return resolve_url("budget:AccountDetail", self.pk)

    @classmethod
    def by_full_no(cls, full_no):
        group_no, account_no = full_no.split('-')
        group_no, account_no = int(group_no), int(account_no)
        default_group_name = "Account group {}".format(group_no)
        group, created = AccountGroup.objects.get_or_create(number=group_no, defaults={'name': default_group_name, 'description': default_group_name})
        default_account_name = "Account {}".format(account_no)
        account, created = cls.objects.get_or_create(group=group, number=account_no,
                                                     defaults={'name': default_account_name, 'description': default_account_name})
        return account


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

    @property
    def account_full_no(self):
        return self.account.full_no

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.available = self.amount - self.spent
        super().save(force_insert, force_update, using, update_fields)

    def update_available(self):
        spent = Application.objects.filter(budget=self, approval=True).aggregate(Sum('amount'))['amount__sum']
        self.spent = spent or 0
        self.save()


def get_workflow():
    return OrderedDict((
        (DecisionKind.manager, settings.BUDGET_MANAGERS_GROUP),
        (DecisionKind.accountant, settings.BUDGET_ACCOUNTANTS_GROUP),
        (DecisionKind.control, settings.BUDGET_CONTROL_GROUP),
    ))


DECISION_GROUPS = SimpleLazyObject(get_workflow)
WORKFLOW = SimpleLazyObject(lambda: tuple((kind for kind, group in DECISION_GROUPS.items())))
CHOICES = SimpleLazyObject(lambda: tuple((item.value, _(ChoicesIntEnum.capitalize(item))) for item in WORKFLOW))


class ApplicationStatus(ChoicesIntEnum):
    open = 100
    placed = 200
    completed = 1000


# A hack to force django to localize enum names
_('Open'), _('Placed'), _('Completed')


class DecisionKind(ChoicesIntEnum):
    manager = 100
    accountant = 200,
    control = 1000,


class Application(BaseModel):
    date = models.DateField(_('date'), help_text=_('Approximate payment due date that will determine the monthly budget.'))
    amount = models.DecimalField(_('amount'), decimal_places=0, max_digits=6, help_text=_('What is the total cost?'))
    title = models.CharField(_('title'), max_length=150, help_text=_('Short distinguishing name for this expenditure'))
    description = models.TextField(_('description'), help_text=_('Please describe and justify this expenditure.'))
    requester = models.ForeignKey(get_user_model(), verbose_name=_('requester'), on_delete=models.PROTECT)
    manager = models.ForeignKey(
        get_user_model(), verbose_name=_('manager'), on_delete=models.PROTECT, related_name='+', limit_choices_to=Q(groups__name='Managers')
    )
    submitted = models.DateField(_('submission date'), auto_now_add=True)
    # accountant = models.ForeignKey(
    #     get_user_model(), on_delete=models.PROTECT, null=True, blank=True,
    #     related_name='+', limit_choices_to=Q(groups__name='Accountants')
    # )
    account = models.ForeignKey(
        Account, verbose_name=_('account'), on_delete=models.CASCADE, null=True, blank=True,
        help_text=_('Please select a budget that need to be decreased'))
    budget = models.ForeignKey(
        Budget, verbose_name=_('budget'), on_delete=models.CASCADE, null=True, blank=True,
        help_text=_('Please select a budget that need to be decreased'))
    # control = models.ForeignKey(
    #     get_user_model(), on_delete=models.PROTECT, null=True, blank=True,
    #     related_name='+', limit_choices_to=Q(groups__name='Controllers')
    # )
    awaiting = models.PositiveSmallIntegerField(_('awaiting decision'), choices=DecisionKind.choices(), null=True, blank=True)
    approval = models.NullBooleanField(_('approval'))
    status = models.PositiveSmallIntegerField(
        _('application status'), help_text=_("Processing status for procurement"),
        choices=ApplicationStatus.choices(), default=int(ApplicationStatus.open)
    )

    class Meta:
        verbose_name = _('application')
        verbose_name_plural = _('applications')
        ordering = '-submitted', 'date',
        permissions = (
            ('change_application_status', _("Can change the application status")),
        )
        index_together = 'submitted', 'date'

    def __str__(self):
        return '{:%Y-%m-%d %H:%M}-{} {:03}'.format(self.date, self.requester, self.amount)

    def get_absolute_url(self):
        return resolve_url("budget:ApplicationDetail", self.pk)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.pk is None and self.awaiting is None:
            self.awaiting = DecisionKind.manager

        if self.account:
            budget = Budget.objects.filter(year=self.date.year, month=self.date.month, account=self.account).first()
            if not budget:
                last_budget = Budget.objects.filter(account=self.account).first()
                amount = last_budget.amount if last_budget else 0
                budget, x = Budget.objects.get_or_create(
                    year=self.date.year,
                    month=self.date.month,
                    account=self.account,
                    defaults={'amount': amount}
                )
            self.budget = budget

        super().save(force_insert, force_update, using, update_fields)

    def can_update(self):
        return not self.decisions.filter(approval__isnull=False).exists()

    def can_change_account(self):
        # After last decision account change is not available
        decision = self.get_decision(WORKFLOW[-1])
        return decision is None or decision.approval is None

    def get_decision(self, kind):
        decisions = {i.kind: i for i in self.all_decisions}
        return decisions.get(kind, None)

    @cached_property
    def all_decisions(self):
        return self.decisions.all()

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

        for kind in WORKFLOW:
            if not self.get_decision(kind):
                self.send_to_group(kind)
                break

    def send_to_group(self, kind):
        users = self.get_users(kind)
        assert users, "No users to send notifications to for kind: {}".format(str(kind))
        for user in users:
            self.send_approval_request(user)

    def get_users(self, kind):
        if kind == DecisionKind.manager:
            return [self.manager]

        group = DECISION_GROUPS[kind]
        log.debug("To group: %s", group)
        group, x = Group.objects.get_or_create(name=group)
        return group.user_set.all()

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

    @classmethod
    def get_next_waiting_application(cls, user):
        return cls.awaiting_decision(user).order_by("-date").first()

    @classmethod
    def awaiting_decision(cls, user):
        q = cls.objects.all().filter(approval__isnull=True)

        f = []
        if user.groups.filter(name=settings.BUDGET_MANAGERS_GROUP).exists():
            f.append(Q(manager=user, awaiting=DecisionKind.manager))

        if user.groups.filter(name=settings.BUDGET_ACCOUNTANTS_GROUP).exists():
            f.append(Q(awaiting=DecisionKind.accountant))

        if user.groups.filter(name=settings.BUDGET_CONTROL_GROUP).exists():
            f.append(Q(awaiting=DecisionKind.control, account__isnull=False))

        f = reduce(lambda x, y: x | y, f)
        return q.filter(f)

    def setup_awaiting_kind(self):
        last_decision = self.decisions.order_by('-kind').filter(approval__isnull=False).first()
        if last_decision is None:
            self.awaiting = DecisionKind.manager
            return

        kinds = DecisionKind.values()
        i = kinds.index(last_decision.kind)
        try:
            self.awaiting = kinds[i + 1]
        except IndexError:
            self.awaiting = None


class Decision(BaseModel):
    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    ts = models.DateTimeField(_('time stamp'), default=datetime.now)
    kind = models.PositiveSmallIntegerField(_('approval step'), choices=DecisionKind.choices())
    approval = models.NullBooleanField(_('approval'))
    notes = models.TextField(_('notes'), null=True, blank=True, help_text="Notatka nie jest wymagana do podjęcia decyzji.")

    class Meta:
        verbose_name = _('decision')
        verbose_name_plural = _('decisions')
        default_related_name = 'decisions'
        unique_together = ('application', 'kind')

    def __str__(self):
        return '{} ({}): {}'.format(self.user, self.kind, self.approval)

    @classmethod
    def clean_decisions(cls, application):
        cls.objects.filter(application=application).update(approval=None)


# noinspection PyUnusedLocal
@receiver(signals.post_save, sender=get_user_model())
def team_membership(sender, instance=None, **kwargs):
    if settings.BUDGET_TEAM_DOMAIN in instance.email:
        from django.contrib.auth.models import Group
        team, new = Group.objects.get_or_create(name='Team')
        team.user_set.add(instance)


# noinspection PyUnusedLocal
@receiver(signals.post_save, sender=Application)
def application_update(sender, instance=None, **kwargs):
    if instance.budget_id is None:
        return
    instance.budget.update_available()


# noinspection PyUnusedLocal
@receiver(signals.post_save, sender=Decision)
def decision_create(sender, instance=None, **kwargs):
    application = instance.application
    application.setup_awaiting_kind()
    application.save()
