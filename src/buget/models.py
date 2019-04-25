# coding=utf-8
# Copyright (c) 2018 Janusz Skonieczny

import logging
from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.shortcuts import resolve_url
from django.utils.translation import ugettext_lazy as _
from django_powerbank.db.models.base import BaseModel

log = logging.getLogger(__name__)


class Account(BaseModel):
    name = models.CharField(_('name'), max_length=255)
    no = models.CharField(_('name'), max_length=255)
    description = models.CharField(_('description'), max_length=255)

    class Meta:
        verbose_name = _('account')
        verbose_name_plural = _('accounts')
        ordering = 'no', 'name',

    def __str__(self):
        return ''.join((self.no, ' ', self.name))

    def get_absolute_url(self):
        return resolve_url("budget:AccountDetail", self.pk)


class Budget(BaseModel):
    account = models.ForeignKey(Account)
    amount = models.DecimalField(_('amount'), default=0)
    spent = models.DecimalField(_('money spent'), default=0)
    available = models.DecimalField(_('money available'))
    year = models.PositiveSmallIntegerField(_('year'), validators=[MaxValueValidator(2100), MinValueValidator(2019)])
    month = models.PositiveSmallIntegerField(_('month'), choices=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12))

    class Meta:
        verbose_name = _('expenses')
        verbose_name_plural = _('expenses')
        ordering = 'yea', 'month',

    def __str__(self):
        return ''.join((self.no, ' ', self.name))

    def get_absolute_url(self):
        return resolve_url("budget:AccountDetail", self.pk)


class ExpenditureRequest(BaseModel):
    amount = models.DecimalField(_('amount'))
    description = models.TextField(_('description'))
    budget = models.ForeignKey(Budget)
    requester = models.ForeignKey(get_user_model())
    manager = models.ForeignKey(get_user_model())
    control = models.ForeignKey(get_user_model())


class SignOff(BaseModel):
    user = models.ForeignKey(get_user_model())
    ts = models.DateTimeField(_('time stamp'), default=datetime.now)
    request = models.ForeignKey(ExpenditureRequest)
