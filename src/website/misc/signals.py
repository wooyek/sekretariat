# coding=utf-8
# Copyright (c) 2018 Janusz Skonieczny

import logging

from django import dispatch

log = logging.getLogger(__name__)

# Clock signals to help you schedule things
# separately from any queueing application like Celery or Redis Queue
signal_every_minute = dispatch.Signal(providing_args=[])
signal_every_hour = dispatch.Signal(providing_args=[])
signal_every_day = dispatch.Signal(providing_args=[])
signal_every_monday = dispatch.Signal(providing_args=[])

# A signal for error handling tests
# raise errors on it and watch how the're handled
signal_raise_error = dispatch.Signal(providing_args=[])
