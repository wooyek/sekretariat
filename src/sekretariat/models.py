# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class SampleModel(models.Model):
    name = models.CharField(max_length=150, verbose_name=_('name'), blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'), on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        default_related_name = "samples"
        verbose_name = _('sample model')
        verbose_name_plural = _('sample models')
