# -*- coding: utf-8 -*-

import maya
from django.conf import settings
from django.db import models
from django.shortcuts import resolve_url
from django.utils import timezone
from django.utils.timezone import get_current_timezone_name
from django.utils.translation import ugettext_lazy as _
from django_powerbank.db.models.base import BaseModel
from django_powerbank.db.models.fields import SecretField

from website.misc.mail import send_mail_template


def text_to_time(text):
    assert text
    assert text.strip()
    tz = get_current_timezone_name()
    try:
        return maya.when(text, timezone=tz).datetime(tz)
    except ValueError as ex:
        raise ValueError(text) from ex


def text_to_times(text):
    def parser(lines):
        last_item = None
        for line in lines.splitlines():
            if not line or not line.strip():
                continue
            line = line.replace(",", ":")
            if line.startswith("\t"):
                line = last_item.strftime("%Y-%m-%d") + line
            last_item = text_to_time(line)
            yield last_item

    return sorted(set(parser(text)))


class OpenOfficeGroup(BaseModel):
    name = models.CharField(max_length=250, verbose_name=_('title'))

    class Meta:
        verbose_name = _('open office group')
        verbose_name_plural = _('open office groups')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return resolve_url("sekretariat:OpenOfficeGroupDetail", self.pk)

    def update_slots(self, text):
        pass


class OpenOfficeSlot(BaseModel):
    group = models.ForeignKey(OpenOfficeGroup, on_delete=models.CASCADE)
    start = models.DateTimeField(verbose_name=_('event start'))
    student = models.CharField(max_length=250, verbose_name=_('student name'), null=True, blank=True)
    email = models.EmailField(max_length=250, verbose_name=_('email'), null=True, blank=True)
    confirmation_secret = SecretField(max_length=200, source_field='email', null=True, blank=True)
    confirmed = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('open office slot')
        verbose_name_plural = _('open office slot')
        ordering = 'start', 'group',
        default_related_name = 'slots'

    def __str__(self):
        return "{:%Y-%m-%d %H:%M} {}".format(self.start, self.group)

    def get_absolute_url(self):
        return resolve_url("sekretariat:OpenOfficeGroupDetail", self.group_id)

    def confirm(self, request):
        self.confirmed = timezone.now()
        self.save()

    def send_message(self, url=None):
        assert self.confirmation_secret, "Secret is missing for email '{}'".format(self.confirmation_email)
        if url is None:
            url = resolve_url("sekretariat:OpenOfficeSlotBookConfirm", pk=self.pk, secret=self.confirmation_secret)
            url = '{base_url}{url}'.format(base_url=settings.BASE_URL, url=url)
        self.confirmation_url = url
        self.save()
        ctx = {
            'person': self.student,
            'start': self.start,
            'email': self.email,
            'action_url': url,
        }
        subject = _("Potwierdzenie terminu").format(**ctx)
        send_mail_template("OpenOfficeSlot/email.html", ctx, subject, to=self.email)
