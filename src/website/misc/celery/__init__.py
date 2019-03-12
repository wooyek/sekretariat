# coding=utf-8
# Copyright (c) 2018 Janusz Skonieczny

import logging

from celery import Celery, signals
from django.conf import settings

log = logging.getLogger(__name__)

app = Celery('website.misc.celery')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
# logging.debug("app.conf.CELERY_ALWAYS_EAGER: %s" % app.conf.CELERY_ALWAYS_EAGER)

from django.apps import apps  # noqa: F402 F403 isort:skip

app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])  # pragma: no branch


@signals.after_setup_logger.connect
def augment_logging_cfg(signal=None, sender=None, logger=None, loglevel=None, logfile=None, format=None, colorize=None, *args, **kargs):  # pragma: no cover
    logging.info("Adding AdminEmailHandler to celery loggers")
    from django.utils.log import AdminEmailHandler
    handler = AdminEmailHandler()
    handler.level = logging.ERROR
    logger.handlers.append(handler)
    logging.info("logger.handlers: %s" % logger.handlers)
    logging.info("settings.ADMINS:%s" % settings.ADMINS)

    import sys
    import os

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
