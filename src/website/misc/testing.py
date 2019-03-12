# coding=utf-8
# Copyright 2015 Brave Labs sp. z o.o.
# All rights reserved.
#
# This source code and all resulting intermediate files are CONFIDENTIAL and
# PROPRIETY TRADE SECRETS of Brave Labs sp. z o.o.
# Use is subject to license terms. See NOTICE file of this project for details.
import logging
import os
import sys
from collections import OrderedDict

import django
from django.apps import apps
from django.conf import settings
from django.utils.functional import empty
from django.utils.timezone import is_aware, make_naive

from website.misc.factories import UserFactory

logging.debug("settings._wrapped: %s", settings._wrapped)

# To avoid any configuration hiccups and all that boilerplate test runner settings
# just to get Django not complain about it being not configured we'll do it here
# now SimpleTestCase should work without any database setup overhead

# noinspection PyProtectedMember
if settings._wrapped is empty:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")
    # noinspection PyProtectedMember
    settings._setup()

if not apps.ready:
    django.setup()

for path in sys.path:
    logging.debug("sys.path: %s", path)

from datetime import date, datetime  # noqa F402 isort:skip
from django.test import Client, TestCase  # noqa F402 isort:skip
from django.test.runner import DiscoverRunner  # noqa F402 isort:skip

# from test_plus import TestCase

from django_powerbank.testing.base import AssertionsMx  # noqa F402 isort:skip


def fake_data(*args, **kwargs):
    fields = dict(((name, name) for name in args))
    fields.update(kwargs)
    return fake_data2(fields)


def fake_data2(fields):
    from faker import Faker
    fake = Faker()
    return OrderedDict(((field, getattr(fake, kind)()) for field, kind in fields.items()))


def model_to_request_data_dict(model):
    """
    Removes fields with None value. Test client will serialize them into 'None' strings that will cause validation errors.
    """
    from django.forms import model_to_dict
    data = model_to_dict(model)
    for k, v in data.copy().items():
        if v is None:
            del data[k]
        from django_powerbank.db.models.fields import ChoicesIntEnum
        if isinstance(v, ChoicesIntEnum):
            data[k] = int(v)
        if isinstance(v, date):
            data[k] = v.isoformat()
        if isinstance(v, datetime):
            if is_aware(v):
                # ISO_INPUT_FORMATS does not conform to what isoformat returns
                data[k] = make_naive(v).isoformat().replace("T", " ")
            else:
                data[k] = v.isoformat()
    return data


class AdminUserTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory.create(is_superuser=True, is_staff=True, username='neo')
        self.client.force_login(self.user, settings.AUTHENTICATION_BACKENDS[0])


class StaffUserTestCase(AssertionsMx, TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory.create(is_superuser=False, is_staff=True)
        self.client.force_login(self.user, settings.AUTHENTICATION_BACKENDS[0])


class UserTestCase(TestCase, AssertionsMx):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory.create()
        self.client.force_login(self.user, settings.AUTHENTICATION_BACKENDS[0])


def staff_client():
    staff = UserFactory.create(is_superuser=False, is_staff=True)
    client = django.test.Client()
    client.force_login(staff, settings.AUTHENTICATION_BACKENDS[0])
    return client


def authenticated_client(user=None):
    user = user or UserFactory.create(is_superuser=False, is_staff=False)
    client = django.test.Client()
    client.force_login(user, settings.AUTHENTICATION_BACKENDS[0])
    return client


class KeepDbTestRunner(DiscoverRunner):
    def __init__(self, **kwargs):
        kwargs['keepdb'] = True
        super(KeepDbTestRunner, self).__init__(**kwargs)
