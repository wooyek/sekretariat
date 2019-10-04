# coding=utf-8
# Copyright (c) 2018 Janusz Skonieczny

import logging

import pytest
from django import test
from django.conf import settings
from django.contrib.auth.models import Group

from website.misc.factories import UserFactory

log = logging.getLogger(__name__)


def get_client(user):
    client = test.Client()
    client.force_login(user, settings.AUTHENTICATION_BACKENDS[0])
    return client


# noinspection PyUnusedLocal
@pytest.fixture
def can_add_application():
    from django.contrib.contenttypes.models import ContentType
    from budget.models import Application
    content_type = ContentType.objects.get_for_model(Application)
    from django.contrib.auth.models import Permission
    permission, created = Permission.objects.get_or_create(codename='add_application', content_type=content_type)
    return permission


@pytest.fixture
def team_user(can_add_application):
    user = UserFactory.create(is_superuser=False, is_staff=False)
    team, new = Group.objects.get_or_create(name=settings.BUDGET_TEAM_GROUP)
    team.permissions.add(can_add_application)
    team.user_set.add(user)
    return user


@pytest.fixture
def team_client(team_user):
    return get_client(team_user)


@pytest.fixture
def accountant(can_add_application):
    user = UserFactory.create(is_superuser=False, is_staff=False)
    team, new = Group.objects.get_or_create(name=settings.BUDGET_ACCOUNTANTS_GROUP)
    team.permissions.add(can_add_application)
    team.user_set.add(user)
    return user


@pytest.fixture
def control(can_add_application):
    user = UserFactory.create(is_superuser=False, is_staff=False)
    team, new = Group.objects.get_or_create(name=settings.BUDGET_CONTROL_GROUP)
    team.permissions.add(can_add_application)
    team.user_set.add(user)
    return user


@pytest.fixture
def accountant_client(accountant):
    client = test.Client()
    client.force_login(accountant, settings.AUTHENTICATION_BACKENDS[0])
    return client


@pytest.fixture
def control_client(control):
    client = test.Client()
    client.force_login(control, settings.AUTHENTICATION_BACKENDS[0])
    return client


@pytest.fixture
def manager(can_add_application):
    user = UserFactory.create(is_superuser=False, is_staff=False)
    team, new = Group.objects.get_or_create(name=settings.BUDGET_MANAGERS_GROUP)
    team.permissions.add(can_add_application)
    team.user_set.add(user)
    return user


@pytest.fixture
def manager_client(manager):
    client = test.Client()
    client.force_login(manager, settings.AUTHENTICATION_BACKENDS[0])
    return client
