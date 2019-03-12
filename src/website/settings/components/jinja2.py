# coding=utf-8
# Copyright 2015 Brave Labs sp. z o.o.
# All rights reserved.
#
# This source code and all resulting intermediate files are CONFIDENTIAL and
# PROPRIETY TRADE SECRETS of Brave Labs sp. z o.o.
# Use is subject to license terms. See NOTICE file of this project for details.

import logging

from . import core

log = logging.getLogger(__name__)

core.TEMPLATES.insert(0, {
    # https://docs.djangoproject.com/en/1.9/topics/templates/#django.template.backends.jinja2.Jinja2
    'BACKEND': 'dinja2.backend.Jinja2Engine',
    'DIRS': [
        str(core.BASE_DIR / 'templates'),
        str(core.BASE_DIR / "templates" / "errors"),
    ],
    'APP_DIRS': True,
    'OPTIONS': {
        'environment': {
            'website.settings.jinja2.environment': {
                # # Match the template names ending in .html but not the ones in the admin folder.
                # "match_extension": ".html",
                # "app_dirname": "jinja2",
                # # Can be set to "jinja2.Undefined" or any other subclass.
                # "undefined": "jinja2.Undefined",
                # "newstyle_gettext": True,
                # "tests": {},
                # "filters": {},
                # "globals": {},
                # "constants": {},
                # "extensions": [
                #     "jinja2.ext.do",
                #     "jinja2.ext.loopcontrols",
                #     "jinja2.ext.with_",
                #     "jinja2.ext.i18n",
                #     "jinja2.ext.autoescape",
                #     "django_jinja.builtins.extensions.CsrfExtension",
                #     "django_jinja.builtins.extensions.CacheExtension",
                #     "django_jinja.builtins.extensions.TimezoneExtension",
                #     "django_jinja.builtins.extensions.UrlsExtension",
                #     "django_jinja.builtins.extensions.StaticFilesExtension",
                #     "django_jinja.builtins.extensions.DjangoFiltersExtension",
                # ],
                # "bytecode_cache": {
                #     "name": "default",
                #     "backend": "django_jinja.cache.BytecodeCache",
                #     "enabled": False,
                # },
                # "autoescape": True,
                # "auto_reload": DEBUG,
                # "translation_engine": "django.utils.translation",
            }
        },
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.template.context_processors.csrf',
            # 'django.template.context_processors.i18n',
            'django.template.context_processors.tz',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
            'website.settings.context_processor',
        ],
    },
})
