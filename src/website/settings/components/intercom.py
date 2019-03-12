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

INTERCOM_APP_ID = core.env("INTERCOM_APP_ID")
INTERCOM_APP_SECRET = bytearray(core.env("INTERCOM_APP_SECRET"), 'ascii')
