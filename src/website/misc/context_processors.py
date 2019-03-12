# coding=utf-8
# Copyright 2015 Brave Labs sp. z o.o.
# All rights reserved.
#
# This source code and all resulting intermediate files are CONFIDENTIAL and
# PROPRIETY TRADE SECRETS of Brave Labs sp. z o.o.
# Use is subject to license terms. See NOTICE file of this project for details.

import functools
import logging
import platform
import subprocess

import django
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.utils.deprecation import MiddlewareMixin

from website import __version__


def website_settings(request):
    from django.conf import settings

    return {
        'settings': settings,
    }


def system_info(request):
    return {
        'system': get_system_info()
    }


def current_site(request):  # noqa
    return {
        'site': get_current_site(request),
    }


@functools.lru_cache(maxsize=1)
def get_website_version():
    try:
        from raven import fetch_git_sha
        from raven.exceptions import InvalidGitRepository
        try:
            return fetch_git_sha(str(settings.BASE_DIR))[:5]
        except InvalidGitRepository:
            return ''
    except ImportError:  # noqa
        command = 'git rev-parse HEAD'
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, cwd=str(settings.BASE_DIR))
        return process.communicate()[0].decode()


@functools.lru_cache(maxsize=1)
def get_system_info():
    DJANGO_VERSION = django.get_version()
    PY_VERSION = platform.python_version()
    try:
        SOURCE_VERSION = get_website_version() or settings.SOURCE_VERSION[:5]
    except Exception as ex:  # noqa
        logging.error("", exc_info=ex)
        SOURCE_VERSION = settings.SOURCE_VERSION[:5]
    return {
        'django': DJANGO_VERSION,
        'python': PY_VERSION,
        'website': __version__,
        'revision': SOURCE_VERSION,
    }


class SystemInfoMiddleware(MiddlewareMixin):
    """Updates context_data with sidebar definition"""

    def process_template_response(self, request, response):
        # https://docs.djangoproject.com/en/1.10/topics/http/middleware/#process-template-response
        if hasattr(response, 'context_data'):
            response.context_data.update(system_info(request))
        return response
