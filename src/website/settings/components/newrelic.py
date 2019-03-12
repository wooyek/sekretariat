# coding=utf-8
# Copyright (c) 2018 Janusz Skonieczny

import logging

from . import core

log = logging.getLogger(__name__)

core.LOGGING['loggers']['newrelic'] = {
    'handlers': ['console'],
    'propagate': True,
    'level': 'WARNING',
}
