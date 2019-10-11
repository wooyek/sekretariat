# -*- coding: utf-8 -*-
from datetime import timedelta

import django_filters
import reversion
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect, resolve_url
from django.utils import timezone
from django.views.generic.base import ContextMixin
from django_filters.views import FilterMixin
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


class PermissionRequiredView(AbstractAuthorizedView):
    """Verify that the current user has all specified permissions."""
    permission_required = None

    def get_permission_required(self):
        """
        Override this method to override the permission_required attribute.
        Must return an iterable.
        """
        if self.permission_required is None:
            raise ImproperlyConfigured(
                '{0} is missing the permission_required attribute. Define {0}.permission_required, or override '
                '{0}.get_permission_required().'.format(self.__class__.__name__)
            )
        if isinstance(self.permission_required, str):
            perms = (self.permission_required,)
        else:
            perms = self.permission_required
        return perms

    def is_authorized(self, *args, **kwargs):
        """
        Override this method to customize the way permissions are checked.
        """
        perms = self.get_permission_required()
        return self.request.user.has_perms(perms)


class ApplicationFilter(django_filters.FilterSet):
    class Meta:
        model = models.Application
        fields = ['approval', ]  # 'decisions__approval']
        # fields = {
        #     'approval': ['isnull', ],
        #     'decisions__approval': ['exact', 'year__gt'],
        # }


class FilterViewMixin(FilterMixin, ContextMixin):

    def get_context_data(self, **kwargs):
        filterset_class = self.get_filterset_class()
        # noinspection PyAttributeOutsideInit
        self.filter = self.get_filterset(filterset_class)

        if not self.filter.is_bound or self.filter.is_valid() or not self.get_strict():
            kwargs['object_list'] = self.filter.qs
        else:
            # noinspection PyAttributeOutsideInit
            kwargs['object_list'] = self.filter.queryset.none()

        kwargs['filter'] = self.filter
        return super().get_context_data(**kwargs)


class ApplicationListUser(AbstractAuthorizedView, FilterViewMixin, PaginationMixin, ListView):
    model = models.Application
    paginate_by = 25

    def is_authorized(self, *args, **kwargs):
        user = self.request.user
        return user.pk == self.kwargs['pk'] or user.is_staff

    def get_queryset(self):
        queryset = super().get_queryset().filter(Q(requester_id=self.kwargs['pk']) | Q(manager_id=self.kwargs['pk']))
        return queryset

    # def get_context_data(self, *, object_list=None, **kwargs):
    #     kwargs['filter'] = ApplicationFilter(self.request.GET, queryset=models.Application.objects.all())
    #     return super().get_context_data(object_list=object_list, **kwargs)


class ApplicationList(PermissionRequiredView, FilterViewMixin, PaginationMixin, ListView):
    model = models.Application
    ordering = 'date'
    paginate_by = 25
    permission_required = 'budget.view_application'

    def is_authorized(self, *args, **kwargs):
        return is_operations(self.request.user)

    def handle_forbidden(self):
        if self.request.user.has_perms(['budget.add_application']):
            return redirect("budget:ApplicationListUser", self.request.user.pk)
        return super(ApplicationList, self).handle_forbidden()

    def get_context_data(self, *, object_list=None, **kwargs):
        kwargs['filter'] = ApplicationFilter(self.request.GET, queryset=models.Application.objects.all())
        return super().get_context_data(object_list=object_list, **kwargs)


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
            return self.to_decision(sign_off, int(kind))

        if not self.request.user.is_staff:
            return super(ApplicationDetail, self).handle_forbidden()

    def get_decision_kind(self):
        if self.request.user.groups.filter(name=settings.BUDGET_CONTROL_GROUP).exists():
            return models.DecisionKind.control
        if self.request.user.groups.filter(name=settings.BUDGET_ACCOUNTANTS_GROUP).exists():
            return models.DecisionKind.accountant
        if self.request.user == self.object.manager:
            return models.DecisionKind.manager

    def to_decision(self, decision, kind):
        if decision:
            return redirect('budget:DecisionUpdate', decision.pk, kind)
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
        with reversion.create_revision():
            valid = super().form_valid(form)
            reversion.set_user(self.request.user)
            reversion.set_comment("Application created")
        form.instance.send_notifications()
        msg = 'Zapotrzebowanie "{}" zostało zapisane.'.format(self.object.title)
        messages.success(self.request, msg)
        return valid


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
        with reversion.create_revision():
            valid = super().form_valid(form)
            reversion.set_user(self.request.user)
            reversion.set_comment("Application updated")
        form.instance.send_notifications()
        msg = 'Zapotrzebowanie "{}" zostało zaktualizowane.'.format(self.object.title)
        messages.success(self.request, msg)
        return valid

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
            msg = 'Nie ma więcej decyzji do podjęcia.'
            messages.success(self.request, msg)
            return resolve_url("budget:ApplicationList")

        msg = 'Podejmij następną decyzję.'
        messages.info(self.request, msg)
        decision = next.decisions.filter(kind=self.kind).first()
        if decision:
            return resolve_url("budget:DecisionUpdate", decision.pk, self.kind)
        return resolve_url("budget:DecisionCreate", next.pk, self.kind)


class DecisionCreate(DecisionBase, CreateView):

    def form_valid(self, form):
        with reversion.create_revision():
            valid = super().form_valid(form)
            reversion.set_user(self.request.user)
            reversion.set_comment("Decision created")
            msg = 'Decyzja dla "{}" została dodana.'.format(self.application.title)
            messages.success(self.request, msg)
            return valid


class DecisionUpdate(DecisionBase, UpdateView):

    def form_valid(self, form):
        with reversion.create_revision():
            valid = super().form_valid(form)
            reversion.set_user(self.request.user)
            reversion.set_comment("Decision updated")
            msg = 'Decyzja dla "{}" została zaktualizowana.'.format(self.application.title)
            messages.success(self.request, msg)
            return valid

    # noinspection PyAttributeOutsideInit
    def setup_expenditure(self):
        self.object = self.get_object()
        self.application = self.object.application
