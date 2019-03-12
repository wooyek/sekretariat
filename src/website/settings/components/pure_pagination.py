# coding=utf-8
# Copyright (c) 2018 Janusz Skonieczny

import logging

from . import core

log = logging.getLogger(__name__)

core.INSTALLED_APPS += (
    'pure_pagination',
)

PAGINATION_SETTINGS = {
    'PAGE_RANGE_DISPLAYED': 10,
    'MARGIN_PAGES_DISPLAYED': 2,
    'SHOW_FIRST_PAGE_WHEN_INVALID': True,
}
