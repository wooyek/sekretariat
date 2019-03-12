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

core.INSTALLED_APPS += (
    'django.contrib.gis',
)

if core.DATABASES['default']['ENGINE'] == 'django.contrib.gis.db.backends.postgis':
    core.DATABASES['default']['OPTIONS']['options'] = '-c search_path=gis,public,pg_catalog'
elif core.DATABASES['default']['ENGINE'] == 'django.contrib.gis.db.backends.spatialite':
    SPATIALITE_LIBRARY_PATH = 'mod_spatialite'
