# -*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.shortcuts import redirect, resolve_url
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from django_powerbank.views import Http403
from django_powerbank.views.auth import StaffRequiredMixin
from pascal_templates import ListView, UpdateView, CreateView
from pascal_templates.views import DetailView

from . import forms, models


class BudgetList(ListView):
    model = models.Budget


class BudgetDetail(DetailView):
    model = models.Budget


class BudgetCreate(CreateView):
    model = models.Budget


class BudgetUpdate(UpdateView):
    model = models.Budget

