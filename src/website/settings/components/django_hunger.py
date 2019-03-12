# coding=utf-8
# Copyright (c) 2018 Janusz Skonieczny
"""
Django-hunger provides a flexible private beta phase for Django projects.

https://django-hunger.readthedocs.io/en/latest/quickstart.html
"""
import logging

from . import core

log = logging.getLogger(__name__)

#

core.MIDDLEWARE += (  # noqa: F405
    'django_hunger2.middleware.BetaMiddleware',
)

core.INSTALLED_APPS += (
    'django_hunger2',
)

HUNGER_ALWAYS_ALLOW_MODULES = [
    'django.contrib.auth.views',
]

HUNGER_ALWAYS_ALLOW_VIEWS = (
    'moniuszko_cms:HomeView',
    'moniuszko_cms:PleaseWaitView',
)

HUNGER_REDIRECT = 'moniuszko_cms:PleaseWaitView'
