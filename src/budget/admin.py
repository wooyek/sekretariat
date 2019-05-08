# coding=utf-8
# Copyright (c) 2018 Janusz Skonieczny

import logging, sys, os, pathlib

log = logging.getLogger(__name__)
# coding=utf-8
from django.contrib import admin
from import_export.admin import ImportExportMixin

from website.misc.admin import DynamicLookupMixin
from . import models, resources


class SignOffInline(admin.TabularInline):
    model = models.Decision


@admin.register(models.Application)
class ApplicationAdmin(ImportExportMixin, DynamicLookupMixin, admin.ModelAdmin):
    list_display = ('amount', 'description', 'budget', 'requester', 'manager',)
    list_filter = ('budget__account',)
    inlines = [SignOffInline]


@admin.register(models.Budget)
class BudgetAdmin(ImportExportMixin, DynamicLookupMixin, admin.ModelAdmin):
    resource_class = resources.BudgetResource
    list_display = ('__str__', 'account', 'amount', 'spent', 'available')
    list_filter = ('account',)


@admin.register(models.Account)
class AccountAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('__str__', 'group', 'number', 'description')
    list_filter = ('group',)


@admin.register(models.AccountGroup)
class AccountGroupAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('__str__', 'description')


@admin.register(models.Decision)
class SignOffAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('ts', 'request', 'user', 'kind', 'approval')
    list_filter = ('user', 'kind', 'approval')
    date_hierarchy = 'ts'

