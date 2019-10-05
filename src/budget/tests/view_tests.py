# coding=utf-8
import logging

import faker
import pytest
from budget.tests.conftest import get_client
from django import test
from django.shortcuts import resolve_url
from mock import patch
from pytest_lazyfixture import lazy_fixture

from website.misc.testing import assert_no_form_errors, model_to_request_data_dict
from .. import models, views
from . import factories

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


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyProtectedMember
@pytest.mark.django_db
@pytest.mark.parametrize(
    "factory", LIST_FACTORIES
)
class UpdateViewTests(object):

    def test_anonymous(self, factory):
        item = factory()
        model_name = factory._meta.model.__name__
        url = resolve_url("budget:{}Update".format(model_name), item.pk)
        response = test.Client().get(url)
        assert response.status_code == 302

    def test_get(self, factory, admin_client):
        item = factory()
        model_name = factory._meta.model.__name__
        url = resolve_url("budget:{}Update".format(model_name), item.pk)
        response = admin_client.get(url)
        assert response.status_code == 403


@pytest.mark.django_db
class ExpenditureCreateViewTests(object):

    def test_post(self, team_client, manager):
        item = factories.ApplicationFactory(manager=manager)
        url = resolve_url("budget:ApplicationCreate")
        data = model_to_request_data_dict(item)
        data['manager'] = item.manager_id
        response = team_client.post(url, data=data)
        assert_no_form_errors(response)
        assert response.status_code == 302


# noinspection PyMethodMayBeStatic
@pytest.mark.django_db
class ApplicationAccountViewTests(object):
    def test_get(self, team_user):
        item = factories.ApplicationFactory(requester=team_user)
        url = resolve_url("budget:ApplicationAccount", item.pk)
        response = get_client(team_user).get(url)
        assert response.status_code == 200
        assert len(response.context_data['messages']) == 0

    @pytest.mark.parametrize(
        "kind, approval, ok", [
            (models.DecisionKind.manager, True, False),
            (models.DecisionKind.manager, False, False),
            (models.DecisionKind.manager, None, True),
            (models.DecisionKind.accountant, True, False),
            (models.DecisionKind.accountant, False, False),
            (models.DecisionKind.accountant, None, True),
        ]
    )
    def test_with_decissions(self, kind, approval, ok, team_user):
        decission = factories.DecisionFactory(
            kind=kind, approval=approval, application__requester=team_user,
        )
        url = resolve_url("budget:ApplicationAccount", decission.application.pk)
        response = get_client(team_user).get(url)
        assert response.status_code == 200
        assert len(response.context_data['messages']) == 0

    def test_with_decisions(self, team_user):
        decission = factories.DecisionFactory(
            kind=models.DecisionKind.control,
            application__requester=team_user,
        )
        url = resolve_url("budget:ApplicationAccount", decission.application.pk)
        response = get_client(team_user).get(url)
        assert response.status_code == 200
        messages = [m.message for m in response.context_data['messages']]
        msg = messages[0]
        log.debug("msg: %s", msg)
        assert msg.startswith('Zmiana zapotrzebowania skutkuje')

    @pytest.mark.parametrize(
        "kind, approval, result", [
            (models.DecisionKind.manager, True, True),
            (models.DecisionKind.manager, False, False),
            (models.DecisionKind.manager, None, None),
            (models.DecisionKind.accountant, True, True),
            (models.DecisionKind.accountant, False, False),
            (models.DecisionKind.accountant, None, None),
            (models.DecisionKind.control, True, None),
            (models.DecisionKind.control, False, None),
            (models.DecisionKind.control, None, None),
        ]
    )
    def test_process_decisions(self, kind, approval, result):
        decision = factories.DecisionFactory(
            kind=kind, approval=approval
        )
        view = views.ApplicationAccount()
        view.process_decisions(decision.application)
        decision.refresh_from_db()
        assert decision.approval is result


# noinspection PyMethodMayBeStatic
@pytest.mark.django_db
class ApplicationUpdateViewTest(object):

    @patch("budget.models.Application.send_approval_request")
    def test_post(self, send_approval_request, accountant, manager):
        item = factories.ApplicationFactory(manager=manager)
        url = resolve_url("budget:ApplicationUpdate", item.pk)
        data = model_to_request_data_dict(item)
        data['manager'] = item.manager_id
        response = get_client(item.requester).post(url, data=data)
        assert_no_form_errors(response)
        assert response.status_code == 302

        assert send_approval_request.called
        assert send_approval_request.call_count == 1
        args, kwargs = send_approval_request.call_args
        assert manager == args[0]

    @pytest.mark.parametrize(
        "kind, approval, result", [
            (models.DecisionKind.manager, True, None),
            (models.DecisionKind.manager, False, None),
            (models.DecisionKind.manager, None, None),
            (models.DecisionKind.accountant, True, None),
            (models.DecisionKind.accountant, False, None),
            (models.DecisionKind.accountant, None, None),
            (models.DecisionKind.control, True, None),
            (models.DecisionKind.control, False, None),
            (models.DecisionKind.control, None, None),
        ]
    )
    def test_process_decisions(self, kind, approval, result):
        decision = factories.DecisionFactory(
            kind=kind, approval=approval
        )
        view = views.ApplicationUpdate()
        view.process_decisions(decision.application)
        decision.refresh_from_db()
        assert decision.approval is result

    def test_get(self, team_user):
        item = factories.ApplicationFactory(requester=team_user)
        url = resolve_url("budget:ApplicationUpdate", item.pk)
        response = get_client(team_user).get(url)
        assert response.status_code == 200
        assert len(response.context_data['messages']) == 0

    def test_with_decisions(self, team_user):
        decission = factories.DecisionFactory(
            kind=models.DecisionKind.manager,
            application__requester=team_user,
        )
        url = resolve_url("budget:ApplicationUpdate", decission.application.pk)
        response = get_client(team_user).get(url)
        assert response.status_code == 200
        messages = [m.message for m in response.context_data['messages']]
        msg = messages[0]
        log.debug("msg: %s", msg)
        assert msg.startswith('Zmiana zapotrzebowania skutkuje')

    def test_anonymous(self):
        item = factories.ApplicationFactory()
        url = resolve_url("budget:ApplicationUpdate", item.pk)
        response = test.Client().get(url)
        assert response.status_code == 302

    def test_forbidden(self, authenticated_client):
        item = factories.ApplicationFactory()
        url = resolve_url("budget:ApplicationUpdate", item.pk)
        response = authenticated_client.get(url)
        assert response.status_code == 403

    def test_staff_get(self, staff_client):
        item = factories.ApplicationFactory()
        url = resolve_url("budget:ApplicationUpdate", item.pk)
        response = staff_client.get(url)
        assert response.status_code == 403

    def test_control_get(self, control):
        item = factories.ApplicationFactory()
        url = resolve_url("budget:ApplicationUpdate", item.pk)
        response = get_client(control).get(url)
        assert response.status_code == 200

    def test_accountant_get(self, accountant):
        item = factories.ApplicationFactory()
        url = resolve_url("budget:ApplicationUpdate", item.pk)
        response = get_client(accountant).get(url)
        assert response.status_code == 200


# noinspection PyMethodMayBeStatic
@pytest.mark.django_db
class ApplicationListUserTests(object):

    def test_redirect_to_user_list(self, team_user):
        url = resolve_url("budget:ApplicationList")
        response = get_client(team_user).get(url)
        assert_no_form_errors(response)
        assert response.status_code == 302
        assert response.url == resolve_url("budget:ApplicationListUser", team_user.pk)

    def test_get(self, team_user):
        url = resolve_url("budget:ApplicationListUser", team_user.pk)
        response = get_client(team_user).get(url)
        assert response.status_code == 200

    def test_anonymous(self):
        url = resolve_url("budget:ApplicationListUser", 666)
        response = test.Client().get(url)
        assert response.status_code == 302

    def test_forbidden(self, authenticated_client):
        url = resolve_url("budget:ApplicationListUser", 666)
        response = authenticated_client.get(url)
        assert response.status_code == 403

    def test_staff_get(self, staff_client):
        url = resolve_url("budget:ApplicationListUser", 666)
        response = staff_client.get(url)
        assert response.status_code == 200


# noinspection PyMethodMayBeStatic
@pytest.mark.django_db
class ApplicationDetailTest(object):

    def test_anonymous(self, client):
        item = factories.ApplicationFactory()
        url = resolve_url("budget:ApplicationDetail", item.pk)
        response = client.get(url)
        assert response.status_code == 302

    def test_admin(self, admin_client):
        item = factories.ApplicationFactory()
        url = resolve_url("budget:ApplicationDetail", item.pk)
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_team(self, team_client):
        item = factories.ApplicationFactory()
        url = resolve_url("budget:ApplicationDetail", item.pk)
        response = team_client.get(url)
        assert response.status_code == 403

    def test_accountant(self, accountant_client):
        item = factories.ApplicationFactory()
        url = resolve_url("budget:ApplicationDetail", item.pk)
        response = accountant_client.get(url)
        assert response.status_code == 302
        assert response.url == resolve_url("budget:DecisionCreate", item.pk, int(models.DecisionKind.accountant))

    def test_control(self, control_client):
        item = factories.ApplicationFactory()
        url = resolve_url("budget:ApplicationDetail", item.pk)
        response = control_client.get(url)
        assert response.status_code == 302
        assert response.url == resolve_url("budget:DecisionCreate", item.pk, int(models.DecisionKind.control))

    def test_accountant_update(self, accountant_client):
        item = factories.DecisionFactory(kind=models.DecisionKind.accountant)
        url = resolve_url("budget:ApplicationDetail", item.application_id)
        response = accountant_client.get(url)
        assert response.status_code == 302
        assert response.url == resolve_url("budget:DecisionUpdate", item.pk, int(models.DecisionKind.accountant))

    def test_control_update(self, control_client):
        item = factories.DecisionFactory(kind=models.DecisionKind.control)
        url = resolve_url("budget:ApplicationDetail", item.application_id)
        response = control_client.get(url)
        assert response.status_code == 302
        assert response.url == resolve_url("budget:DecisionUpdate", item.pk, int(models.DecisionKind.control))


# noinspection PyMethodMayBeStatic
@pytest.mark.django_db
class DecisionUpdateViewTests(object):
    def test_anonymous(self, client):
        item = factories.DecisionFactory()
        url = resolve_url("budget:DecisionUpdate", item.pk, int(models.DecisionKind.control))
        response = client.get(url)
        assert response.status_code == 302

    def test_admin(self, admin_client):
        item = factories.DecisionFactory()
        url = resolve_url("budget:DecisionUpdate", item.pk, int(models.DecisionKind.control))
        response = admin_client.get(url)
        assert response.status_code == 403

    def test_team(self, team_client):
        item = factories.DecisionFactory()
        url = resolve_url("budget:DecisionUpdate", item.pk, int(models.DecisionKind.control))
        response = team_client.get(url)
        assert response.status_code == 403

    def test_accountant(self, accountant_client):
        item = factories.DecisionFactory()
        url = resolve_url("budget:DecisionUpdate", item.pk, int(models.DecisionKind.control))
        response = accountant_client.get(url)
        assert response.status_code == 403

    def test_accountant2(self, accountant_client):
        item = factories.DecisionFactory()
        url = resolve_url("budget:DecisionUpdate", item.pk, int(models.DecisionKind.accountant))
        response = accountant_client.get(url)
        assert response.status_code == 200

    def test_control(self, control_client):
        item = factories.DecisionFactory()
        url = resolve_url("budget:DecisionUpdate", item.pk, int(models.DecisionKind.accountant))
        response = control_client.get(url)
        assert response.status_code == 403

    def test_control2(self, control_client):
        item = factories.DecisionFactory()
        url = resolve_url("budget:DecisionUpdate", item.pk, int(models.DecisionKind.control))
        response = control_client.get(url)
        assert response.status_code == 200


# noinspection PyMethodMayBeStatic
@pytest.mark.django_db
class DecisionCreateViewTests(object):
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
        next = factories.DecisionFactory(kind=models.DecisionKind.accountant).application
        item = factories.ApplicationFactory()
        control = int(models.DecisionKind.control)
        url = resolve_url("budget:DecisionCreate", item.pk, control)
        response = control_client.post(url, data={'approval': 'approve'})
        assert_no_form_errors(response)
        assert response.status_code == 302
        assert resolve_url("budget:DecisionCreate", next.pk, control) == response.url
        decission = item.get_decision(control)
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
        assert resolve_url("budget:ApplicationList") == response.url
        decission = item.application.get_decision(control)
        assert decission is not None
        assert decission.approval is False

    def test_success_url_create_next(self):
        item = factories.DecisionFactory(kind=models.DecisionKind.manager).application
        view = views.DecisionBase()
        view.kind = int(models.DecisionKind.accountant)
        assert view.get_success_url() == resolve_url("budget:DecisionCreate", item.pk, int(models.DecisionKind.accountant))

    def test_success_url_update_next(self):
        item = factories.DecisionFactory(kind=models.DecisionKind.accountant, approval=None)
        view = views.DecisionBase()
        view.kind = int(models.DecisionKind.accountant)
        assert view.get_success_url() == resolve_url("budget:DecisionUpdate", item.pk, int(models.DecisionKind.accountant))

    def test_success_url_list(self):
        view = views.DecisionBase()
        view.kind = int(models.DecisionKind.accountant)
        assert view.get_success_url() == resolve_url("budget:ApplicationList")


@pytest.mark.django_db
@pytest.mark.parametrize(
    'client, expenditures', [
        (lazy_fixture('admin_client'), True),
        (lazy_fixture('team_client'), True),
        (lazy_fixture('accountant_client'), True),
        (lazy_fixture('control_client'), True),
    ]
)
class HomeViewTest(object):
    # noinspection PyMethodMayBeStatic
    def test_applications_visible(self, client, expenditures):
        url = resolve_url("HomeView")
        response = client.get(url)
        assert response.status_code == 200
        assert ('<h5 class="card-header">Expenditures</h5>' in str(response.content)) is expenditures
        assert ('Expenditures</a>' in str(response.content)) is expenditures
