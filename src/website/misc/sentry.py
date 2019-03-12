# coding=utf-8
# Copyright (c) 2018 Janusz Skonieczny

import logging

log = logging.getLogger(__name__)


class SentryLogFilter(logging.Filter):
    def __init__(self, exclude_loggers=None):
        self.exclude_loggers = exclude_loggers

    def filter(self, record):
        if self.exclude_loggers is None:  # pragma: no cover
            return True
        return record.name not in self.exclude_loggers  # pragma: no cover
