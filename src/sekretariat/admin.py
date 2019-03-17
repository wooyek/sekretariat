# coding=utf-8
from django.contrib import admin
from import_export.admin import ImportExportMixin

from website.misc.admin import DynamicLookupMixin
from . import models


class OpenOfficeSlotInline(admin.TabularInline):
    model = models.OpenOfficeSlot


@admin.register(models.OpenOfficeGroup)
class OpenOfficeGroupAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    inlines = (OpenOfficeSlotInline,)


@admin.register(models.OpenOfficeSlot)
class OpenOfficeSlotAdmin(ImportExportMixin, DynamicLookupMixin, admin.ModelAdmin):
    list_display = ('start', 'student', 'email', 'group__name', 'confirmed')
    list_filter = ('group',)
    date_hierarchy = 'start'
