# coding=utf-8
import logging

import faker
import pytest
from django import test
from django.conf import settings
from django.contrib.auth.models import Group
from django.shortcuts import resolve_url

from website.misc.factories import UserFactory
from website.misc.testing import assert_no_form_errors, model_to_request_data_dict
from . import factories
from .. import models

log = logging.getLogger(__name__)
fake = faker.Faker()

LIST_FACTORIES = (
    # factories.AccountFactory,
    # factories.AccountGroupFactory,
    # factories.BudgetFactory,
    factories.ApplicationFactory,
)

DETAIL_FACTORIES = (
    # factories.AccountFactory,
    # factories.AccountGroupFactory,
    # factories.BudgetFactory,
    factories.ApplicationFactory,
)


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyProtectedMember
@pytest.mark.django_db
@pytest.mark.parametrize(
    "factory", DETAIL_FACTORIES
)
class DetailViewsTests(object):

    def test_anonymous(self, client, factory):
        item = factory()
        url = item.get_absolute_url()
        response = client.get(url)
        assert response.status_code == 302

    def test_forbidden(self, admin_client, factory):
        item = factory()
        url = item.get_absolute_url()
        log.debug("url: %s", url)
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_get(self, staff_client, factory):
        item = factory()
        url = item.get_absolute_url()
        log.debug("url: %s", url)
        response = staff_client.get(url)
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
        url = resolve_url("budget:{}List".format(model_name))
        response = test.Client().get(url)
        assert response.status_code == 302

    def test_forbidden(self, factory, admin_client):
        factory.create_batch(25)
        model_name = factory._meta.model.__name__
        url = resolve_url("budget:{}List".format(model_name))
        response = admin_client.get(url)
        assert response.status_code == 302

    def test_get(self, factory, staff_client):
        factory.create_batch(25)
        model_name = factory._meta.model.__name__
        url = resolve_url("budget:{}List".format(model_name))
        response = staff_client.get(url)
        assert response.status_code == 403

    def test_control(self, factory, control_client):
        factory.create_batch(25)
        model_name = factory._meta.model.__name__
        url = resolve_url("budget:{}List".format(model_name))
        response = control_client.get(url)
        assert response.status_code == 200

    def test_accountint(self, factory, accountant_client):
        factory.create_batch(25)
        model_name = factory._meta.model.__name__
        url = resolve_url("budget:{}List".format(model_name))
        response = accountant_client.get(url)
        assert response.status_code == 200


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyProtectedMember
@pytest.mark.django_db
@pytest.mark.parametrize(
    "factory", LIST_FACTORIES
)
class CreateViewTests(object):

    def test_anonymous(self, factory):
        model_name = factory._meta.model.__name__
        url = resolve_url("budget:{}Create".format(model_name))
        response = test.Client().get(url)
        assert response.status_code == 302

    def test_get(self, factory, admin_client):
        model_name = factory._meta.model.__name__
        url = resolve_url("budget:{}Create".format(model_name))
        response = admin_client.get(url)
        assert response.status_code == 403


@pytest.mark.django_db
class ExpenditureCreateViewTests(object):

    def test_post(self, team_client):
        item = factories.ApplicationFactory()
        url = resolve_url("budget:ApplicationCreate")
        data = model_to_request_data_dict(item)
        response = team_client.post(url, data=data)
        assert_no_form_errors(response)
        assert response.status_code == 302


# noinspection PyUnusedLocal
@pytest.fixture
def team_client():
    user = UserFactory.create(is_superuser=False, is_staff=False)
    team, new = Group.objects.get_or_create(name=settings.BUDGET_TEAM_GROUP)
    team.user_set.add(user)
    client = test.Client()
    client.force_login(user, settings.AUTHENTICATION_BACKENDS[0])
    return client


@pytest.fixture
def accountant_client():
    user = UserFactory.create(is_superuser=False, is_staff=False)
    team, new = Group.objects.get_or_create(name=settings.BUDGET_ACCOUNTANTS_GROUP)
    team.user_set.add(user)
    client = test.Client()
    client.force_login(user, settings.AUTHENTICATION_BACKENDS[0])
    return client


@pytest.fixture
def control_client():
    user = UserFactory.create(is_superuser=False, is_staff=False)
    team, new = Group.objects.get_or_create(name=settings.BUDGET_CONTROL_GROUP)
    team.user_set.add(user)
    client = test.Client()
    client.force_login(user, settings.AUTHENTICATION_BACKENDS[0])
    return client


@pytest.fixture
def manager_client():
    user = UserFactory.create(is_superuser=False, is_staff=False)
    team, new = Group.objects.get_or_create(name=settings.BUDGET_CONTROL_GROUP)
    team.user_set.add(user)
    client = test.Client()
    client.force_login(user, settings.AUTHENTICATION_BACKENDS[0])
    return client


# noinspection PyMethodMayBeStatic
@pytest.mark.django_db
class SignOffCreateViewTests(object):
    def test_anonymous(self, client):
        item = factories.ApplicationFactory()
        url = resolve_url("budget:DecisionCreate", item.pk, int(models.DecisionKind.manager))
        response = client.get(url)
        assert response.status_code == 302

    def test_admin(self, admin_client):
        item = factories.ApplicationFactory()
        url = resolve_url("budget:DecisionCreate", item.pk, int(models.DecisionKind.manager))
        response = admin_client.get(url)
        assert response.status_code == 403

    def test_team(self, team_client):
        item = factories.ApplicationFactory()
        url = resolve_url("budget:DecisionCreate", item.pk, int(models.DecisionKind.manager))
        response = team_client.get(url)
        assert response.status_code == 403

    def test_accountant(self, accountant_client):
        item = factories.ApplicationFactory()
        url = resolve_url("budget:DecisionCreate", item.pk, int(models.DecisionKind.accountant))
        response = accountant_client.get(url)
        assert response.status_code == 200

    def test_control(self, control_client):
        item = factories.ApplicationFactory()
        url = resolve_url("budget:DecisionCreate", item.pk, int(models.DecisionKind.control))
        response = control_client.get(url)
        assert response.status_code == 200

    def test_approve(self, control_client):
        item = factories.ApplicationFactory()
        control = int(models.DecisionKind.control)
        url = resolve_url("budget:DecisionCreate", item.pk, control)
        response = control_client.post(url, data={'approval': 'approve'})
        assert_no_form_errors(response)
        item = models.Decision.objects.first()
        assert response.status_code == 302
        assert resolve_url("budget:DecisionUpdate", control, item.pk) == response.url
        decission = item.request.get_decision(control)
        assert decission is not None
        assert decission.approval is True

    def test_reject(self, control_client):
        item = factories.ApplicationFactory()
        control = int(models.DecisionKind.control)
        url = resolve_url("budget:DecisionCreate", item.pk, control)
        response = control_client.post(url, data={'approval': 'reject'})
        assert_no_form_errors(response)
        item = models.Decision.objects.first()
        assert response.status_code == 302
        assert resolve_url("budget:DecisionUpdate", control, item.pk) == response.url
        decission = item.request.get_decision(control)
        assert decission is not None
        assert decission.approval is False
