# coding=utf-8
from import_export import resources

from . import models


class OpenOfficeSlotResource(resources.ModelResource):
    class Meta:
        model = models.OpenOfficeSlot
