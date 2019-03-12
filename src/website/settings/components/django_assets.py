# coding=utf-8
# Copyright 2015 Brave Labs sp. z o.o.
# All rights reserved.
#
# This source code and all resulting intermediate files are CONFIDENTIAL and
# PROPRIETY TRADE SECRETS of Brave Labs sp. z o.o.
# Use is subject to license terms. See NOTICE file of this project for details.

import logging
import os

from . import core

log = logging.getLogger(__name__)

core.INSTALLED_APPS += (
    'django_assets',
)

# django-assets
# http://django-assets.readthedocs.org/en/latest/settings.html

ASSETS_LOAD_PATH = core.STATIC_ROOT
ASSETS_ROOT = str(core.BASE_DIR / 'assets' / "compressed")
ASSETS_DEBUG = core.env('ASSETS_DEBUG', bool, default=core.DEBUG)  # Disable when testing compressed file in DEBUG mode
if ASSETS_DEBUG:  # pragma: no cover
    ASSETS_URL = core.STATIC_URL
    ASSETS_MANIFEST = "json:{}".format(os.path.join(ASSETS_ROOT, "manifest.json"))
else:
    ASSETS_URL = core.STATIC_URL + "assets/compressed/"
    ASSETS_MANIFEST = "json:{}".format(os.path.join(core.STATIC_ROOT, 'assets', "compressed", "manifest.json"))
ASSETS_AUTO_BUILD = ASSETS_DEBUG
ASSETS_MODULES = ('website.assets',)
