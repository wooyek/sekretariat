# coding=utf-8
# Copyright (c) 2018 Janusz Skonieczny

import logging

from . import models

log = logging.getLogger(__name__)


def budget(request):
    return {
        'decision_kinds':  models.CHOICES
    }
