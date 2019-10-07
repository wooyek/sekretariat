# coding=utf-8
# Copyright (c) 2018 Janusz Skonieczny

import logging

# coding=utf-8
from django.contrib import admin
from import_export.admin import ImportExportMixin
from reversion.admin import VersionAdmin

from website.misc.admin import DynamicLookupMixin
from . import models, resources

log = logging.getLogger(__name__)


class DecisionInline(admin.TabularInline):
    model = models.Decision


@admin.register(models.Application)
class ApplicationAdmin(ImportExportMixin, DynamicLookupMixin, VersionAdmin):
    list_display = ('date', 'approval', 'pk', 'title', 'amount', 'budget', 'requester', )
    list_filter = ('approval', 'budget__account', 'requester')
    inlines = [DecisionInline]
    date_hierarchy = 'date'


@admin.register(models.Budget)
class BudgetAdmin(ImportExportMixin, DynamicLookupMixin, VersionAdmin):
    resource_class = resources.BudgetResource
    list_display = ('__str__', 'account', 'amount', 'spent', 'available')
    list_filter = ('account',)


@admin.register(models.Account)
class AccountAdmin(ImportExportMixin, VersionAdmin):
    list_display = ('__str__', 'group', 'number', 'description')
    list_filter = ('group',)


@admin.register(models.AccountGroup)
class AccountGroupAdmin(ImportExportMixin, VersionAdmin):
    list_display = ('__str__', 'description')


@admin.register(models.Decision)
class DecisionAdmin(ImportExportMixin, VersionAdmin):
    list_display = ('ts', 'application', 'user', 'kind', 'approval')
    list_filter = ('user', 'kind', 'approval')
    date_hierarchy = 'ts'
