# -*- coding: utf-8 -*-
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect, resolve_url
from django.utils import timezone
from django_powerbank.views import Http400
from django_powerbank.views.auth import AbstractAuthorizedView
from pascal_templates import CreateView, ListView, UpdateView
from pascal_templates.views import DetailView
from pure_pagination import PaginationMixin

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


class ApplicationListUser(AbstractAuthorizedView, PaginationMixin, ListView):
    model = models.Application
    paginate_by = 25

    def is_authorized(self, *args, **kwargs):
        user = self.request.user
        return user.pk == self.kwargs['pk'] or user.is_staff

    def get_queryset(self):
        queryset = super().get_queryset().filter(Q(requester_id=self.kwargs['pk']) | Q(manager_id=self.kwargs['pk']))
        return queryset


class ApplicationList(OperationsRequired, PaginationMixin, ListView):
    model = models.Application
    paginate_by = 25

    def handle_forbidden(self):
        if self.request.user.has_perms(['budget.add_application']):
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
    fields = 'amount', 'date', 'title', 'description', 'manager',

    def get_initial(self):
        return {
            'date': (timezone.now() + timedelta(days=7)).date()
        }

    def form_valid(self, form):
        form.instance.requester = self.request.user
        try:
            return super().form_valid(form)
        finally:
            form.instance.send_notifications()


class ApplicationUpdateBase(AbstractAuthorizedView, UpdateView):
    model = models.Application

    def is_authorized(self, *args, **kwargs):
        user = self.request.user
        return user == self.get_object().requester or is_operations(user)

    def decisions_clean_required(self, item):
        return not item.can_update()

    def get(self, request, *args, **kwargs):
        r = super().get(request, *args, **kwargs)
        if self.decisions_clean_required(self.object):
            messages.warning(request, "Zmiana zapotrzebowania skutkuje anulowaniem wszystkich decyzji. "
                                      "Prośby o podjęcie decyzji zostaną wysłane ponownie. "
                                      "Cofnij w przeglądarce by anulować operację."
                             )
        return r

    def form_valid(self, form):
        item = form.instance
        self.process_decisions(item)
        try:
            return super().form_valid(form)
        finally:
            form.instance.send_notifications()

    def process_decisions(self, item):
        if self.decisions_clean_required(item):
            models.Decision.clean_decisions(item)
        item.approval = None


class ApplicationAccount(ApplicationUpdateBase):
    fields = 'account', 'date',

    def decisions_clean_required(self, item):
        return not item.can_change_account()


class ApplicationUpdate(ApplicationUpdateBase):
    fields = 'amount', 'date', 'title', 'description', 'manager',


class DecisionBase(AbstractAuthorizedView):
    model = models.Decision
    form_class = forms.DecisionForm

    # noinspection PyAttributeOutsideInit
    def is_authorized(self, *args, **kwargs):
        self.setup_expenditure()

        self.kind = self.kwargs['kind']
        if self.kind == models.DecisionKind.manager and self.request.user == self.application.manager:
            return True
        if self.kind == models.DecisionKind.accountant and self.request.user.groups.filter(name=settings.BUDGET_ACCOUNTANTS_GROUP).exists():
            return True
        if self.kind == models.DecisionKind.control and self.request.user.groups.filter(name=settings.BUDGET_CONTROL_GROUP).exists():
            return True
        return False

    def setup_expenditure(self):
        pk = self.kwargs['pk']
        # noinspection PyAttributeOutsideInit
        self.application = models.Application.objects.filter(pk=pk).first()
        if not self.application:
            raise Http400("No expenditure for : {}".format(pk))

    def form_valid(self, form):
        form.instance.user = self.request.user
        application = self.application
        form.instance.application = application
        form.instance.kind = self.kind
        if self.request.POST['approval'] == 'approve':
            form.instance.approval = True
        elif self.request.POST['approval'] == 'reject':
            form.instance.approval = False

        if self.kind == models.DecisionKind.control:
            application.approval = form.instance.approval

        with transaction.atomic():
            try:
                return super().form_valid(form)
            finally:
                application.save()
                application.send_notifications()

    def get_context_data(self, **kwargs):
        kwargs['object'] = self.application
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        next = models.Application.get_next_waiting_application(self.kind)
        if next is None:
            return resolve_url("budget:ApplicationList")

        decision = next.decisions.filter(kind=self.kind).first()
        if decision:
            return resolve_url("budget:DecisionUpdate", decision.pk, self.kind)
        return resolve_url("budget:DecisionCreate", next.pk, self.kind)


class DecisionCreate(DecisionBase, CreateView):
    pass


class DecisionUpdate(DecisionBase, UpdateView):

    # noinspection PyAttributeOutsideInit
    def setup_expenditure(self):
        self.object = self.get_object()
        self.application = self.object.application
