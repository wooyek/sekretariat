# coding=utf-8
import logging

import faker
import pytest
from django import test
from django.shortcuts import resolve_url

from .. import factories

log = logging.getLogger(__name__)
fake = faker.Faker()

FACTORIES = (
    factories.OpenOfficeGroupFactory,
    factories.OpenOfficeSlotFactory,
)

FACTORIES_LIST = (
    factories.OpenOfficeGroupFactory,
)


def get_item_detail_url(factory):
    item = factory()
    if hasattr(item, 'get_absolute_url'):
        url = item.get_absolute_url()
    else:
        # noinspection PyProtectedMember
        model_name = factory._meta.model.__name__
        view_name = "sekretariat:{}Detail".format(model_name)
        url = resolve_url(view_name, item.pk)
    log.debug("url: %s", url)
    return url


def get_model_url(factory, view_suffix):
    # noinspection PyProtectedMember
    model_name = factory._meta.model.__name__
    return resolve_url("sekretariat:{}{}".format(model_name, view_suffix))


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyProtectedMember
@pytest.mark.django_db
@pytest.mark.parametrize(
    "factory", FACTORIES
)
class DetailViewsTests(object):

    def test_anonymous(self, client, factory):
        url = get_item_detail_url(factory)
        response = client.get(url)
        assert 200 == response.status_code

    def test_get(self, admin_client, factory):
        url = get_item_detail_url(factory)
        response = admin_client.get(url)
        assert response.status_code == 200

    # def test_forbidden(self, client, factory):
    #     url = get_item_detail_url(factory)
    #     response = client.get(url)
    #     assert response.status_code == 403


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyProtectedMember
@pytest.mark.django_db
@pytest.mark.parametrize(
    "factory", FACTORIES_LIST
)
class ListViewTests(object):

    def test_anonymous(self, factory):
        factory.create_batch(25)
        url = get_model_url(factory, 'List')
        response = test.Client().get(url)
        assert response.status_code == 302

    def test_get(self, factory, admin_client):
        factory.create_batch(25)
        url = get_model_url(factory, 'List')
        response = admin_client.get(url, follow=True)
        assert response.status_code == 200


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyProtectedMember
@pytest.mark.django_db
@pytest.mark.parametrize(
    "factory", []
)
class CreateViewTests(object):
    def test_anonymous(self, factory):
        url = get_model_url(factory, 'Create')
        response = test.Client().get(url)
        assert response.status_code == 302

    def test_get(self, factory, admin_client):
        url = get_model_url(factory, 'Create')
        response = admin_client.get(url)
        assert response.status_code == 200

    # def test_post(self, factory):
    #     url = get_model_url(factory, 'Create')
    #     response = self.client.post(url, data={
    #         'user': self.user.pk
    #     })
    #     item = models.SampleModel.objects.first()
    #     self.assertRedirects(response, resolve_url('sekretariat:SampleDetail', item.pk), fetch_redirect_response=False)
