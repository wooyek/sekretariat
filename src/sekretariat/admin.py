# coding=utf-8
from django.contrib import admin
from import_export.admin import ImportExportMixin

from . import models, resources


@admin.register(models.SampleModel)
class SampleModelAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = resources.SampleModelResource
    list_display = ('name', )
    list_filter = ('name', )
    readonly_fields = ('name', )
    # date_hierarchy = 'ts'
