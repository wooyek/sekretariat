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

# https://github.com/django-import-export/django-import-export/issues/72#issuecomment-157112447
# IMPORT_EXPORT_TMP_STORAGE_CLASS = 'misc.storage.Utf8TempFolderStorage'

core.INSTALLED_APPS += (
    'import_export',
)
