# coding=utf-8
# Copyright (c) 2018 Janusz Skonieczny

import logging

import pytest
from mock import patch

from . import factories
from .. import models

log = logging.getLogger(__name__)


# noinspection PyMethodMayBeStatic
@pytest.mark.django_db
class ApplicationTest(object):
    @patch("budget.models.Application.send_approval_request")
    def test_send_to_accountant(self, send_approval_request, accountant):
        item = factories.ApplicationFactory()
        item.send_notifications()
        assert send_approval_request.called
        assert send_approval_request.call_count == 1
        args, kwargs = send_approval_request.call_args
        assert accountant == args[0]

    @patch("budget.models.Application.send_approval_request")
    def test_send_to_manager(self, send_approval_request, accountant):
        item = factories.DecisionFactory()
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
