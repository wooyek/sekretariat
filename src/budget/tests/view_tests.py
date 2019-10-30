# coding=utf-8
import logging

import faker
import pytest
from django import test
from django.http import HttpRequest
from django.shortcuts import resolve_url
from mock import MagicMock, patch
from pytest_lazyfixture import lazy_fixture

from budget.tests.conftest import get_client
from website.misc.testing import assert_no_form_errors, model_to_request_data_dict
from . import factories
from .. import models, views

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
class CreateViewTest(object):

    def test_anonymous(self, factory):
        model_name = factory._meta.model.__name__
        url = resolve_url("budget:{}Create".format(model_name))
        response = test.Client().get(url)
        assert response.status_code == 302

    def test_forbidden(self, factory, admin_client):
        model_name = factory._meta.model.__name__
        url = resolve_url("budget:{}Create".format(model_name))
        response = admin_client.get(url)
        assert response.status_code == 403

    def test_get(self, factory, team_client):
        model_name = factory._meta.model.__name__
        url = resolve_url("budget:{}Create".format(model_name))
        response = team_client.get(url)
        assert response.status_code == 200


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyProtectedMember
@pytest.mark.django_db
@pytest.mark.parametrize(
    "factory", LIST_FACTORIES
)
class UpdateViewTest(object):

    def test_anonymous(self, factory):
        item = factory()
        model_name = factory._meta.model.__name__
        url = resolve_url("budget:{}Update".format(model_name), item.pk)
        response = test.Client().get(url)
        assert response.status_code == 302

    def test_forbidden(self, factory, admin_client):
        item = factory()
        model_name = factory._meta.model.__name__
        url = resolve_url("budget:{}Update".format(model_name), item.pk)
        response = admin_client.get(url)
        assert response.status_code == 403

    def test_get(self, factory, team_client):
        item = factory()
        model_name = factory._meta.model.__name__
        url = resolve_url("budget:{}Update".format(model_name), item.pk)
        response = team_client.get(url)
        assert response.status_code == 403


@pytest.mark.django_db
class ApplicationCreateViewTest(object):

    def test_post(self, team_client, manager):
        item = factories.ApplicationFactory(manager=manager)
        url = resolve_url("budget:ApplicationCreate")
        data = model_to_request_data_dict(item)
        data['manager'] = item.manager_id
        response = team_client.post(url, data=data)
        assert_no_form_errors(response)
        assert response.status_code == 302
        assert models.DecisionKind.manager == models.Application.objects.exclude(pk=item.pk).first().awaiting


# noinspection PyMethodMayBeStatic
@pytest.mark.django_db
class ApplicationAccountViewTest(object):
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
class ApplicationStatusViewTest(object):

    @pytest.mark.parametrize(
        "status", [
            models.ApplicationStatus.open,
            models.ApplicationStatus.placed,
            models.ApplicationStatus.completed,
        ]
    )
    def test_post(self, procurement, status):
        item = factories.ApplicationFactory()
        url = resolve_url("budget:ApplicationStatus", item.pk)
        response = get_client(procurement).post(url, data={'status': int(status)})
        assert_no_form_errors(response)
        assert response.status_code == 302
        assert response.url == resolve_url("budget:ApplicationList") + "?approval=true"
        item.refresh_from_db()
        assert item.status == status

    def test_get(self, team_user):
        url = resolve_url("budget:ApplicationStatus", 666)
        response = get_client(team_user).get(url)
        assert response.status_code == 403

    def test_anonymous(self):
        url = resolve_url("budget:ApplicationStatus", 666)
        response = test.Client().get(url)
        assert response.status_code == 302

    def test_forbidden(self, authenticated_client):
        url = resolve_url("budget:ApplicationStatus", 666)
        response = authenticated_client.get(url)
        assert response.status_code == 403

    def test_staff_get(self, staff_client):
        url = resolve_url("budget:ApplicationStatus", 666)
        response = staff_client.get(url)
        assert response.status_code == 403


# noinspection PyMethodMayBeStatic
@pytest.mark.django_db
class ApplicationListUserTest(object):

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


# noinspection PyMethodMayBeStatic,DuplicatedCode
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

    def test_control_as_manager(self, control):
        item = factories.ApplicationFactory(manager=control)
        url = resolve_url("budget:ApplicationDetail", item.pk)
        response = get_client(control).get(url)
        assert response.status_code == 302
        assert response.url == resolve_url("budget:DecisionCreate", item.pk, int(models.DecisionKind.manager))

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
class DecisionUpdateViewTest(object):
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
        account = factories.AccountFactory()
        item = factories.DecisionFactory(application__account=account)
        url = resolve_url("budget:DecisionUpdate", item.pk, int(models.DecisionKind.accountant))
        response = accountant_client.get(url)
        assert response.status_code == 200
        assert 'Change account or date' in str(response.content)

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

    def test_other_manager(self, manager_client):
        item = factories.ApplicationFactory()
        url = resolve_url("budget:DecisionCreate", item.pk, int(models.DecisionKind.manager))
        response = manager_client.get(url)
        assert response.status_code == 403

    def test_manager(self):
        item = factories.ApplicationFactory()
        url = resolve_url("budget:DecisionCreate", item.pk, int(models.DecisionKind.manager))
        response = get_client(item.manager).get(url)
        assert response.status_code == 200

    def test_control(self, control_client):
        item = factories.ApplicationFactory()
        url = resolve_url("budget:DecisionCreate", item.pk, int(models.DecisionKind.control))
        response = control_client.get(url)
        assert response.status_code == 200

    # noinspection PyUnusedLocal
    def test_control_as_manager(self, control, accountant):
        item = factories.ApplicationFactory(manager=control)
        url = resolve_url("budget:DecisionCreate", item.pk, int(models.DecisionKind.manager))
        response = get_client(control).post(url, data={'approval': 'approve'})
        assert response.status_code == 302
        assert item.decisions.filter(kind=models.DecisionKind.manager).first() is not None
        assert item.decisions.filter(kind=models.DecisionKind.control).first() is None

    def test_approve(self, control_client):
        waiting = factories.DecisionFactory(kind=models.DecisionKind.accountant, application__account=factories.AccountFactory()).application
        item = factories.ApplicationFactory(account=factories.AccountFactory())
        control = int(models.DecisionKind.control)
        url = resolve_url("budget:DecisionCreate", item.pk, control)
        response = control_client.post(url, data={'approval': 'approve'})
        assert_no_form_errors(response)
        assert response.status_code == 302
        assert response.url == resolve_url("budget:DecisionCreate", waiting.pk, control)
        decision = item.get_decision(control)
        assert decision is not None
        assert decision.approval is True

    def test_reject(self, control_client):
        item = factories.ApplicationFactory()
        control = int(models.DecisionKind.control)
        url = resolve_url("budget:DecisionCreate", item.pk, control)
        response = control_client.post(url, data={'approval': 'reject'})
        assert_no_form_errors(response)
        item = models.Decision.objects.first()
        assert response.status_code == 302
        assert resolve_url("budget:ApplicationList") == response.url
        decision = item.application.get_decision(control)
        assert decision is not None
        assert decision.approval is False

    def test_success_url_create_next(self, accountant):
        item = factories.DecisionFactory(kind=models.DecisionKind.manager, application__account=factories.AccountFactory()).application
        view = views.DecisionBase()
        view.request = MagicMock(HttpRequest())
        view.request._messages = MagicMock()
        view.request.user = accountant
        view.kind = int(models.DecisionKind.accountant)
        assert view.get_success_url() == resolve_url("budget:DecisionCreate", item.pk, int(models.DecisionKind.accountant))

    def test_success_url_update_next(self, accountant):
        item = factories.DecisionFactory(kind=models.DecisionKind.accountant, approval=None, application__account=factories.AccountFactory())
        factories.DecisionFactory(kind=models.DecisionKind.manager, application=item.application)
        view = views.DecisionBase()
        view.request = MagicMock(HttpRequest())
        view.request._messages = MagicMock()
        view.request.user = accountant
        view.kind = int(models.DecisionKind.accountant)
        assert view.get_success_url() == resolve_url("budget:DecisionUpdate", item.pk, int(models.DecisionKind.accountant))

    def test_success_url_list(self, accountant):
        view = views.DecisionBase()
        view.kind = int(models.DecisionKind.accountant)
        view.request = MagicMock(HttpRequest())
        view.request._messages = MagicMock()
        view.request.user = accountant
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
