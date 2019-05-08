# coding=utf-8
# Copyright (c) 2018 Janusz Skonieczny

import logging

import django.test
import pytest
from django.conf import settings

from website.misc.factories import UserFactory

log = logging.getLogger(__name__)


@pytest.fixture
def staff_client():
    staff = UserFactory.create(is_superuser=False, is_staff=True)
    client = django.test.Client()
    client.force_login(staff, settings.AUTHENTICATION_BACKENDS[0])
    return client


@pytest.fixture
def authenticated_client(user=None):
    user = user or UserFactory.create(is_superuser=False, is_staff=False)
    client = django.test.Client()
    client.force_login(user, settings.AUTHENTICATION_BACKENDS[0])
    return client
