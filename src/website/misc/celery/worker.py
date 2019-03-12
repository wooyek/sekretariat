# coding=utf-8
# Copyright (c) 2018 Janusz Skonieczny

from __future__ import absolute_import

import getpass
import logging
import os
import sys

log = logging.getLogger(__name__)

logging.basicConfig(format='%(asctime)s %(levelname)-7s %(thread)-5d %(filename)s:%(lineno)s | %(funcName)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger().setLevel(logging.DEBUG)
logging.disable(logging.NOTSET)


def setup():
    logging.info("Celery user: %s" % getpass.getuser())
    logging.info("DJANGO_SETTINGS_MODULE: %s" % os.environ.get('DJANGO_SETTINGS_MODULE', 'NOT-SET'))

    # Show a debugging info on console
    logging.debug("__file__ = %s", __file__)
    logging.debug("sys.version = %s", sys.version)
    logging.debug("os.getpid() = %s", os.getpid())
    logging.debug("os.getcwd() = %s", os.getcwd())
    logging.debug("os.curdir = %s", os.curdir)
    logging.debug("sys.path:\n\t%s", "\n\t".join(sys.path))
    logging.debug("PYTHONPATH:\n\t%s", "\n\t".join(os.environ.get('PYTHONPATH', "").split(';')))
    logging.debug("sys.modules.keys() = %s", repr(sys.modules.keys()))
    logging.debug("sys.modules.has_key('website') = %s", 'website' in sys.modules)
    if 'website' in sys.modules:
        logging.debug("sys.modules['website'].__name__ = %s", sys.modules['website'].__name__)
        logging.debug("sys.modules['website'].__file__ = %s", sys.modules['website'].__file__)

    from django.conf import settings  # noqa F402 F403 isort:skip
    import django  # noqa F402 F403 isort:skip

    django.setup()
    logging.debug("settings.__dir__: %s", settings.__dir__())
    logging.debug("settings.DEBUG: %s", settings.DEBUG)

    # When website.celery.worker is used as a worker app
    # Celery will look for app attribute in this module

    # hack to workaround celery removing cwd from sys.path
    # https://github.com/celery/celery/issues/3150
    # import dinja2

    # from website.logcfg import trace_disabled_loggers
    # trace_disabled_loggers()


def run():
    setup()
    from celery import __main__
    __main__.main()
    logging.info("Celery worker exiting...")


if __name__ == '__main__':
    run()
