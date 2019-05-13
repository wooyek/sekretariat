# coding=utf-8
# Copyright (c) 2018 Janusz Skonieczny

import logging

import pytest
from mock import patch

from . import factories

log = logging.getLogger(__name__)


@pytest.mark.django_db
class ApplicationTest(object):
    @patch("budget.models.Application.send_notifications")
    def test_send_to_manager(self, send_notifications):
        factories.ApplicationFactory()
        assert send_notifications.called
