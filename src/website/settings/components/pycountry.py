# coding=utf-8
# Copyright 2015 Brave Labs sp. z o.o.
# All rights reserved.
#
# This source code and all resulting intermediate files are CONFIDENTIAL and
# PROPRIETY TRADE SECRETS of Brave Labs sp. z o.o.
# Use is subject to license terms. See NOTICE file of this project for details.

import logging
from pathlib import Path

import pycountry

from . import core

log = logging.getLogger(__name__)

# https://docs.djangoproject.com/en/1.9/topics/i18n/translation/#how-django-discovers-language-preference
core.LOCALE_PATHS += (str(Path(pycountry.__file__).parent / 'locales'),)
