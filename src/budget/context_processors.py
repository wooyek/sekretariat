# coding=utf-8
# Copyright (c) 2018 Janusz Skonieczny

import logging

from budget.models import DecisionKind

log = logging.getLogger(__name__)


def budget(request):
    return {
        'decision_kinds': DecisionKind.choices()
    }
