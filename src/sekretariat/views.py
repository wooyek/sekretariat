# -*- coding: utf-8 -*-
from django.contrib import messages
from django.shortcuts import redirect, resolve_url
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from django_powerbank.views import Http403
from pascal_templates import ListView, UpdateView
from pascal_templates.views import DetailView

from . import forms, models


class OpenOfficeGroupDetail(DetailView):
    model = models.OpenOfficeGroup


class OpenOfficeGroupList(ListView):
    model = models.OpenOfficeGroup

    def get(self, request, *args, **kwargs):
        item = models.OpenOfficeGroup.objects.first()
        url = resolve_url("sekretariat:OpenOfficeGroupDetail", pk=item.pk)
        return redirect(url)


class OpenOfficeSlotBook(UpdateView):
    model = models.OpenOfficeSlot
    form_class = forms.OpenOfficeSlotForm

    def get(self, request, *args, **kwargs):
        item = self.get_object()
        if item.email:
            messages.warning(self.request, "Przepraszamy ten termin został zajęty przez kogoś innego. Proszę wybrać inny termin.")
            return redirect("sekretariat:OpenOfficeGroupDetail", pk=item.group_id)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        valid = super().form_valid(form)
        self.object.send_message()
        return valid

    def get_success_url(self):
        return resolve_url("sekretariat:OpenOfficeSlotBookSuccess", pk=self.object.pk)


class OpenOfficeSlotBookSuccess(TemplateView):
    template_name = "OpenOfficeSlot/success.html"


class OpenOfficeSlotBookConfirm(DetailView):
    model = models.OpenOfficeSlot
    form_class = forms.OpenOfficeSlotConfirm
    template_name = "OpenOfficeSlot/confirm.html"

    def dispatch(self, request, *args, **kwargs):
        self.validate_secret(request, kwargs['secret'])
        return super().dispatch(request, *args, **kwargs)

    def validate_secret(self, request, confirmation_secret):
        item = self.get_object()
        if item.confirmation_secret != confirmation_secret:
            msg = _("Activation authentication failed")
            raise Http403(msg)

        if item.user.is_active and item.user.has_usable_password():
            msg = _("This activation link was already used")
            raise Http403(msg)

    def post(self, request, *args, **kwargs):
        self.get_object().confirm(self.request)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return resolve_url("accounts:UserSettingsDetail", self.get_object().user_id)
