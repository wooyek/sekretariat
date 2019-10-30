# coding=utf-8
# Copyright (c) 2018 Janusz Skonieczny

import logging

import pendulum
import pytest
from mock import patch

from .. import models
from . import factories

log = logging.getLogger(__name__)


# noinspection PyMethodMayBeStatic
@pytest.mark.django_db
class ApplicationTest(object):
    @patch("budget.models.Application.send_approval_request")
    def test_send_to_accountant(self, send_approval_request, accountant):
        item = factories.DecisionFactory(kind=models.DecisionKind.manager)
        item.application.send_notifications()
        assert send_approval_request.called
        assert send_approval_request.call_count == 1
        args, kwargs = send_approval_request.call_args
        assert accountant == args[0]

    @patch("budget.models.Application.send_approval_request")
    def test_send_to_manager(self, send_approval_request, accountant):
        item = factories.DecisionFactory(kind=models.DecisionKind.accountant)
        item.application.send_notifications()
        assert send_approval_request.called
        assert send_approval_request.call_count == 1
        args, kwargs = send_approval_request.call_args
        assert item.application.manager == args[0]

    @patch("budget.models.Application.send_approval_request")
    def test_send_to_control(self, send_approval_request, accountant, control):
        item = factories.DecisionFactory(kind=models.DecisionKind.manager)
        factories.DecisionFactory(application=item.application)
        item.application.send_notifications()
        assert send_approval_request.called
        assert send_approval_request.call_count == 1
        args, kwargs = send_approval_request.call_args
        assert control == args[0]

    def test_get_manager(self):
        item = factories.ApplicationFactory()
        users = item.get_users(models.DecisionKind.manager)
        assert [item.manager] == users

    def test_get_accountatnts(self, accountant):
        item = factories.ApplicationFactory()
        users = item.get_users(models.DecisionKind.accountant)
        assert [accountant] == list(users)

    def test_get_control(self, control):
        item = factories.ApplicationFactory()
        users = item.get_users(models.DecisionKind.control)
        assert list(users) == [control]

    def test_empty_budget_lists(self, manager):
        item = factories.ApplicationFactory()
        account = factories.AccountFactory()
        item.account = account
        item.save()

    @pytest.mark.parametrize(
        "kind, approval, ok", [
            (models.DecisionKind.manager, True, True),
            (models.DecisionKind.accountant, True, True),
            (models.DecisionKind.control, True, False),
            (models.DecisionKind.control, False, False),
            (models.DecisionKind.control, None, True),
        ]
    )
    def test_account_change_available(self, kind, approval, ok):
        decision = factories.DecisionFactory(kind=kind, approval=approval)
        assert decision.application.can_change_account() == ok

    @pytest.mark.parametrize(
        "kind, approval, ok", [
            (models.DecisionKind.manager, True, False),
            (models.DecisionKind.manager, False, False),
            (models.DecisionKind.manager, None, True),
            (models.DecisionKind.accountant, True, False),
            (models.DecisionKind.accountant, False, False),
            (models.DecisionKind.accountant, None, True),
            (models.DecisionKind.control, True, False),
            (models.DecisionKind.control, False, False),
            (models.DecisionKind.control, None, True),
        ]
    )
    def test_update_possible(self, kind, approval, ok):
        decision = factories.DecisionFactory(kind=kind, approval=approval)
        assert decision.application.can_update() == ok

    def test_next(self, accountant):
        account = factories.AccountFactory()
        factories.DecisionFactory(kind=models.DecisionKind.accountant, application__date=pendulum.today(), application__account=account)
        decision = factories.DecisionFactory(kind=models.DecisionKind.manager, application__date=pendulum.yesterday(), application__account=account)
        item = models.Application.get_next_waiting_application(accountant)
        assert item == decision.application

    def test_next2(self, accountant):
        account = factories.AccountFactory()
        factories.DecisionFactory(kind=models.DecisionKind.accountant, application__date=pendulum.today(), application__account=account)
        decision = factories.DecisionFactory(
            kind=models.DecisionKind.accountant, approval=None, application__date=pendulum.yesterday(),
            application__account=account
        )
        factories.DecisionFactory(kind=models.DecisionKind.manager, application=decision.application)
        item = models.Application.get_next_waiting_application(accountant)
        assert item == decision.application

    def test_no_next(self, accountant):
        account = factories.AccountFactory()
        factories.DecisionFactory(kind=models.DecisionKind.accountant, application__date=pendulum.today(), application__account=account)
        item = models.Application.get_next_waiting_application(accountant)
        assert item is None

    def test_no_next_without_account(self, control):
        factories.DecisionFactory(kind=models.DecisionKind.manager)
        item = models.Application.get_next_waiting_application(control)
        assert item is None

    def test_awaiting_decision_manager(self, manager):
        item = factories.ApplicationFactory(manager=manager)
        assert models.Application.awaiting_decision(item.manager).first() == item

    def test_awaiting_decision_manager_empty(self, manager):
        item = factories.DecisionFactory(application__manager=manager, approval=None).application
        assert models.Application.awaiting_decision(item.manager).first() == item

    def test_awaiting_decision_manager_other(self, manager):
        item = factories.DecisionFactory(
            application__manager=manager, approval=None, kind=models.DecisionKind.accountant
        ).application
        assert models.Application.awaiting_decision(item.manager).first() == item

    def test_awaiting_decision_manager_existing(self, manager):
        item = factories.DecisionFactory(
            application__manager=manager, approval=True, kind=models.DecisionKind.manager
        ).application
        assert models.Application.awaiting_decision(item.manager).first() is None

    def test_setup_awaiting_decision_accountant(self, manager):
        item = factories.DecisionFactory(
            application__manager=manager, approval=True, kind=models.DecisionKind.manager
        ).application
        item.setup_awaiting_kind()
        assert item.awaiting == models.DecisionKind.accountant

    def test_setup_awaiting_decision_control(self, accountant):
        item = factories.DecisionFactory(
            application__manager=accountant, approval=True, kind=models.DecisionKind.accountant
        ).application
        item.setup_awaiting_kind()
        assert item.awaiting == models.DecisionKind.control

    def test_setup_awaiting_decision_none(self, control):
        item = factories.DecisionFactory(
            application__manager=control, approval=True, kind=models.DecisionKind.control
        ).application
        item.setup_awaiting_kind()
        assert item.awaiting is None


# noinspection PyMethodMayBeStatic
@pytest.mark.django_db
class AccountTest(object):
    @pytest.mark.parametrize(
        "full_no", ["400-21", "4-22", "2-22"]
    )
    def test_by_full_no(self, full_no):
        acccount = models.Account.by_full_no(full_no)
        assert acccount is not None
        assert acccount.full_no == full_no

    @pytest.mark.parametrize(
        "full_no", ["0400-21", "500-1", "200-001", ]
    )
    def test_by_full_no2(self, full_no):
        acccount = models.Account.by_full_no(full_no)
        assert acccount is not None
        assert acccount.full_no != full_no

    @pytest.mark.parametrize(
        "full_no", ["-21", "2-", "2", ]
    )
    def test_by_full_no_value_error(self, full_no):
        with pytest.raises(ValueError):
            models.Account.by_full_no(full_no)

    def test_by_full_no_not_create(self):
        item = factories.AccountFactory()
        account = models.Account.by_full_no(item.full_no)
        assert account == item

    def test_by_full_no_not_create_group(self):
        item = factories.AccountGroupFactory()
        account = models.Account.by_full_no("{}-123".format(item.number))
        assert account.group == item
