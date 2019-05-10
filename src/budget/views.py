# -*- coding: utf-8 -*-
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect, resolve_url
from django.utils import timezone
from django_powerbank.views import Http400
from django_powerbank.views.auth import AbstractAuthorizedView
from pascal_templates import CreateView, ListView, UpdateView
from pascal_templates.views import DetailView

from . import forms, models


class TeamRequiredMixin(AbstractAuthorizedView):
    def is_authorized(self, *args, **kwargs):
        return self.request.user.groups.filter(name=settings.BUDGET_TEAM_GROUP).exists()


class AccountantRequiredMixin(AbstractAuthorizedView):
    def is_authorized(self, *args, **kwargs):
        return self.request.user.groups.filter(name=settings.BUDGET_ACCOUNTANTS_GROUP).exists()


class ControlRequiredMixin(AbstractAuthorizedView):
    def is_authorized(self, *args, **kwargs):
        return self.request.user.groups.filter(name=settings.BUDGET_CONTROL_GROUP).exists()


AUTHORIZED_GROUPS = (
    settings.BUDGET_CONTROL_GROUP,
    settings.BUDGET_ACCOUNTANTS_GROUP,
)


class OperationsRequired(AbstractAuthorizedView):
    def is_authorized(self, *args, **kwargs):
        return is_operations(self.request.user)


def is_operations(user):
    return user.groups.filter(name__in=AUTHORIZED_GROUPS).exists()


class BudgetList(OperationsRequired, ListView):
    model = models.Budget


class BudgetDetail(OperationsRequired, DetailView):
    model = models.Budget


class BudgetCreate(OperationsRequired, CreateView):
    model = models.Budget


class BudgetUpdate(OperationsRequired, UpdateView):
    model = models.Budget


class ApplicationListUser(AbstractAuthorizedView, ListView):
    model = models.Application

    def is_authorized(self, *args, **kwargs):
        user = self.request.user
        return user.pk == self.kwargs['pk'] or user.is_staff

    def get_queryset(self):
        queryset = super().get_queryset().filter(Q(requester_id=self.kwargs['pk']) | Q(manager_id=self.kwargs['pk']))
        return queryset


class ApplicationList(OperationsRequired, ListView):
    model = models.Application

    def handle_forbidden(self):
        if self.request.user.has_perms('can_create_application'):
            return redirect("budget:ApplicationListUser", self.request.user.pk)
        return super(ApplicationList, self).handle_forbidden()


class ApplicationDetail(AbstractAuthorizedView, DetailView):
    model = models.Application

    def is_authorized(self, *args, **kwargs):
        # noinspection PyAttributeOutsideInit
        self.object = self.get_object()
        return self.request.user == self.object.requester

    def handle_forbidden(self):

        kind = self.get_decision_kind()
        if kind:
            sign_off = self.object.get_decision(kind)
            return self.to_sign_off(sign_off, int(kind))

        if not self.request.user.is_staff:
            return super(ApplicationDetail, self).handle_forbidden()

    def get_decision_kind(self):
        if self.request.user.groups.filter(name=settings.BUDGET_CONTROL_GROUP).exists():
            return models.DecisionKind.control
        if self.request.user.groups.filter(name=settings.BUDGET_ACCOUNTANTS_GROUP).exists():
            return models.DecisionKind.accountant
        if self.request.user == self.object.manager:
            return models.DecisionKind.manager

    def to_sign_off(self, sign_off, kind):
        if sign_off:
            return redirect('budget:DecisionUpdate', kind, sign_off.pk)
        else:
            return redirect('budget:DecisionCreate', self.object.pk, kind)


class ApplicationCreate(TeamRequiredMixin, CreateView):
    model = models.Application
    fields = 'amount', 'date', 'title', 'description', 'manager', 'account'

    def get_initial(self):
        return {
            'date': (timezone.now() + timedelta(days=7)).date()
        }

    def form_valid(self, form):
        form.instance.requester = self.request.user
        return super().form_valid(form)


class ApplicationUpdate(AbstractAuthorizedView, UpdateView):
    model = models.Application
    fields = 'amount', 'date', 'title', 'description', 'manager', 'account'

    def is_authorized(self, *args, **kwargs):
        user = self.request.user
        return user == self.get_object().requester or is_operations(user)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['account'].readonly = True
        return form

    def form_valid(self, form):
        models.Decision.objects.filter(request=form.instance).update(approval=None)
        form.instance.approval = None
        return super().form_valid(form)


class ApplicationAccount(OperationsRequired, UpdateView):
    model = models.Application
    fields = 'amount', 'date', 'description', 'manager', 'account'

    def is_authorized(self, *args, **kwargs):
        if self.request.user.groups.filter(name=settings.BUDGET_ACCOUNTANTS_GROUP).exists():
            return True


class DecisionBase(AbstractAuthorizedView):
    model = models.Decision
    form_class = forms.DecisionForm

    # noinspection PyAttributeOutsideInit
    def is_authorized(self, *args, **kwargs):
        self.setup_expenditure()

        self.kind = self.kwargs['kind']
        if self.kind == models.DecisionKind.manager and self.request.user == self.expenditure.manager:
            return True
        if self.kind == models.DecisionKind.accountant and self.request.user.groups.filter(name=settings.BUDGET_ACCOUNTANTS_GROUP).exists():
            return True
        if self.kind == models.DecisionKind.control and self.request.user.groups.filter(name=settings.BUDGET_CONTROL_GROUP).exists():
            return True
        return False

    def setup_expenditure(self):
        pk = self.kwargs['pk']
        # noinspection PyAttributeOutsideInit
        self.expenditure = models.Application.objects.filter(pk=pk).first()
        if not self.expenditure:
            raise Http400("No expenditure for : {}".format(pk))

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.request = self.expenditure
        form.instance.kind = self.kind
        if self.request.POST['approval'] == 'approve':
            form.instance.approval = True
        elif self.request.POST['approval'] == 'reject':
            form.instance.approval = False

        if self.kind == models.DecisionKind.control:
            self.expenditure.approval = form.instance.approval

        with transaction.atomic():
            try:
                return super().form_valid(form)
            finally:
                self.expenditure.save()

    def get_context_data(self, **kwargs):
        kwargs['object'] = self.expenditure
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return resolve_url("budget:DecisionUpdate", self.kind, self.object.pk)


class DecisionCreate(DecisionBase, CreateView):
    pass


class DecisionUpdate(DecisionBase, UpdateView):

    # noinspection PyAttributeOutsideInit
    def setup_expenditure(self):
        self.object = self.get_object()
        self.expenditure = self.object.request

    def get_success_url(self):
        return resolve_url("budget:DecisionUpdate", self.kind, self.object.pk)
