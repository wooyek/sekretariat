# -*- coding: utf-8 -*-
from django.shortcuts import resolve_url
from django_powerbank.views.auth import AbstractAuthorizedView, AuthenticatedView
from pascal_templates.views import CreateView, DetailView

from . import models


class SampleCreate(AuthenticatedView, CreateView):
    model = models.SampleModel
    fields = ('name',)

    def get_success_url(self):
        return resolve_url("sekretariat:SampleDetail", self.object.pk)


class SampleDetail(AbstractAuthorizedView, DetailView):
    model = models.SampleModel

    def is_authorized(self, *args, **kwargs):
        return self.get_object().user.pk == self.request.user.pk
