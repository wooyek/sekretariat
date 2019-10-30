# coding=utf-8
# Copyright (c) 2019 Janusz Skonieczny

import logging

import pytest
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.shortcuts import resolve_url

from . import factories

log = logging.getLogger(__name__)

ADMIN_FACTORIES = (
    factories.AccountFactory,
    factories.AccountGroupFactory,
    factories.BudgetFactory,
    factories.ApplicationFactory,
)


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyProtectedMember
@pytest.mark.django_db
@pytest.mark.parametrize(
    "factory", ADMIN_FACTORIES
)
class AdminTests(object):
    def test_changelist(self, factory, admin_client):
        factory()
        url = resolve_url(admin_urlname(factory._meta.model._meta, 'changelist'))
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_change(self, factory, admin_client):
        item = factory()
        url = resolve_url(admin_urlname(factory._meta.model._meta, 'change'), item.pk)
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_add(self, factory, admin_client):
        url = resolve_url(admin_urlname(factory._meta.model._meta, 'add'))
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_delete(self, factory, admin_client):
        item = factory()
        url = resolve_url(admin_urlname(factory._meta.model._meta, 'delete'), item.pk)
        response = admin_client.get(url)
        assert response.status_code == 200
