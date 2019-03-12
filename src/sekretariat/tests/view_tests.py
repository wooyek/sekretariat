# coding=utf-8
import locale
import logging

import faker
import pendulum
import pytest
from django import test
from django.conf import settings
from django.shortcuts import resolve_url
from django.test import RequestFactory, TestCase
from django.utils.text import slugify
from django.utils.timezone import get_current_timezone
from menus.factories import MenuGroupFactory, MenuNodeFactory
from pendulum import UTC
from taggit.models import Tag

from website.misc.testing import UserTestCase
from .. import factories, models, views

log = logging.getLogger(__name__)
fake = faker.Faker()


LIST_FACTORIES = (
    # factories.?,
)

DETAIL_FACTORIES = (
    # factories.?,
)


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyProtectedMember
@pytest.mark.django_db
@pytest.mark.parametrize(
    "factory", DETAIL_FACTORIES
)
class DetailViewsTests(object):

    def test_anonymous(self, client, factory):
        item = factory()
        url = item.get_url()
        response = client.get(url)
        assert response.status_code == 200

    def test_get(self, admin_client, factory):
        item = factory()
        url = item.get_url()
        log.debug("url: %s", url)
        response = admin_client.get(url)
        assert response.status_code == 200


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyProtectedMember
@pytest.mark.django_db
@pytest.mark.parametrize(
    "factory", LIST_FACTORIES
)
class ListViewTests(object):

    def test_anonymous(self, factory):
        factory.create_batch(25)
        model_name = factory._meta.model.__name__
        url = resolve_url("moniuszko_cms:{}List".format(model_name))
        response = test.Client().get(url)
        assert response.status_code == 200

    def test_get(self, factory, admin_client):
        factory.create_batch(25)
        model_name = factory._meta.model.__name__
        url = resolve_url("moniuszko_cms:{}List".format(model_name))
        response = admin_client.get(url)
        assert response.status_code == 200

