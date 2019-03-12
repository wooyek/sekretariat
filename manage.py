#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import logging
import os
import sys
from pathlib import Path

logging.basicConfig(
    format='%(asctime)s %(levelname)-7s %(thread)-5d %(filename)s:%(lineno)s | %(funcName)s | %(message)s',
    # format='%(asctime)s %(levelname)-7s %(thread)-5d %(name)s %(pathname)s:%(lineno)s | %(funcName)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logging.getLogger().setLevel(logging.DEBUG)
logging.disable(logging.NOTSET)
logging.getLogger("PIL.Image").setLevel(logging.WARNING)
logging.getLogger('environ').setLevel(logging.INFO)
logging.debug("Importing: %s" % __file__)
SRC_PATH = str(Path(__file__).parent / 'src')

if __name__ == "__main__":
    if SRC_PATH not in sys.path:
        sys.path.append(SRC_PATH)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
