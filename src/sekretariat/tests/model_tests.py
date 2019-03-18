# coding=utf-8
# Copyright (c) 2018 Janusz Skonieczny

import logging
from datetime import datetime

import pytest
from django.utils.timezone import get_current_timezone

from .. import factories
from ..models import text_to_times

log = logging.getLogger(__name__)

times = ("\n"
         "20.03.2019	10,30\n"
         "	11,30\n"
         "	12,30\n"
         "	13,00\n"
         "	13,30\n"
         "	14,00\n"
         "	14,30\n"
         "	18,00\n"
         "	18,30\n"
         "	19,00\n")

times2 = ("\n"
          "1.03.2019	10,30\n"
          "	11,30\n"
          "21.03.2019	8,00\n"
          "	8,00\n"
          "	8,00,1\n"
          "	8,30\n"
          "	")


# noinspection PyMethodMayBeStatic
class ToTimesTests(object):
    def test_simple(self):
        items = text_to_times("01.03.2019  10:30")
        assert items == [datetime(2019, 3, 1, 10, 30).astimezone(get_current_timezone())]

    def test_multi(self):
        items = text_to_times(times)
        assert items[0] == datetime(2019, 3, 20, 10, 30).astimezone(get_current_timezone())
        assert items[1] == datetime(2019, 3, 20, 11, 30).astimezone(get_current_timezone())
        assert items[2] == datetime(2019, 3, 20, 12, 30).astimezone(get_current_timezone())

    def test_multi2(self):
        items = text_to_times(times2)
        assert items[0] == datetime(2019, 3, 1, 10, 30).astimezone(get_current_timezone())
        assert items[1] == datetime(2019, 3, 1, 11, 30).astimezone(get_current_timezone())
        assert items[2] == datetime(2019, 3, 21, 8, 0).astimezone(get_current_timezone())
        assert items[3] == datetime(2019, 3, 21, 8, 0, 1).astimezone(get_current_timezone())
        assert items[4] == datetime(2019, 3, 21, 8, 30).astimezone(get_current_timezone())


# noinspection PyMethodMayBeStatic
@pytest.mark.django_db
class OpenOfficeGroupTests(object):
    def test_update_slots(self):
        item = factories.OpenOfficeGroupFactory()
        item.update_slots(times)
        assert item.slots.count() == 10

    def test_multi_de_dup(self):
        item = factories.OpenOfficeGroupFactory()
        item.update_slots(times)
        assert item.slots.count() == 10
        item.update_slots(times2 + times)
        assert item.slots.count() == 15
