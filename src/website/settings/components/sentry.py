# coding=utf-8
# Copyright 2015 Brave Labs sp. z o.o.
# All rights reserved.
#
# This source code and all resulting intermediate files are CONFIDENTIAL and
# PROPRIETY TRADE SECRETS of Brave Labs sp. z o.o.
# Use is subject to license terms. See NOTICE file of this project for details.

import logging

from website import __version__
from . import core

log = logging.getLogger(__name__)

core.INSTALLED_APPS += (
    'raven.contrib.django.raven_compat',
)

core.LOGGING['loggers']['raven'] = {
    'level': core.env("SENTRY_LOGGING_LEVEL", default='NOTSET'),
    'handlers': ['console'],
    'propagate': False,
}

core.LOGGING.setdefault('filters', {})['sentry_filter'] = {
    '()': 'website.misc.sentry.SentryLogFilter',
    'exclude_loggers': [
        'backoff',
        'django.security.DisallowedHost'
    ],
}

core.LOGGING['handlers']['sentry'] = {
    'level': 'ERROR',  # To capture more than ERROR, change to WARNING, INFO, etc.
    'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
    'filters': ['sentry_filter'],
    'tags': {
        'env_name': core.ENVIRONMENT_NAME,
        'base_url': core.BASE_URL,
        'log_handler': 'True',
    },
}

root_handlers = core.LOGGING['root']['handlers']
root_handlers.append('sentry')


disable_mail_admins = core.env("SENTRY_CONFIG_DSN", default='').strip() != ''

if core.env("SENTRY_DISABLE_MAIL_ADMINS", default=disable_mail_admins, cast=bool):
    if core.LOGGING['loggers']['django.request']['handlers'] == 'mail_admins':
        # This duplicates sentry functionality
        del core.LOGGING['loggers']['django.request']
    if 'mail_admins' in root_handlers:
        root_handlers.remove('mail_admins')


core.MIDDLEWARE = ('raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',) + core.MIDDLEWARE

RAVEN_CONFIG = {
    'dsn': core.env("SENTRY_CONFIG_DSN"),
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    'release': __version__,
    'tags': {
        'env_name': core.ENVIRONMENT_NAME,
        'base_url': core.BASE_URL,
        'log_handler': 'False',
    },
}

SENTRY_PUBLIC_DSN = core.env("SENTRY_PUBLIC_DSN")
