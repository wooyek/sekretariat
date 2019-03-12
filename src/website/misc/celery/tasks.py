# coding=utf-8
# Copyright 2015 Brave Labs sp. z o.o.
import logging

from celery.app import shared_task
from celery.utils.log import get_task_logger

from website.misc.signals import signal_every_day, signal_every_hour, signal_every_minute, signal_every_monday

log = logging.getLogger(__name__)

logging = get_task_logger(__name__)


@shared_task(bind=False, max_retries=5, queue="clock", trail=False)
def every_minute():
    results = signal_every_minute.send_robust(every_minute)
    for receiver, response in results:
        if isinstance(response, Exception):  # pragma: no cover
            log.error(response, exc_info=(type(response), response, response.__traceback__))


@shared_task(bind=False, max_retries=5, queue="clock", trail=False)
def every_hour():
    results = signal_every_hour.send_robust(every_hour)
    for receiver, response in results:
        if isinstance(response, Exception):  # pragma: no cover
            log.error(response, exc_info=(type(response), response, response.__traceback__))


@shared_task(bind=False, max_retries=5, queue="clock", trail=False)
def every_day():
    results = signal_every_day.send_robust(every_day)
    for receiver, response in results:
        if isinstance(response, Exception):  # pragma: no cover
            log.error(response, exc_info=(type(response), response, response.__traceback__))


@shared_task(bind=False, max_retries=5, queue="clock", trail=False)
def every_monday():
    results = signal_every_monday.send_robust(every_monday)
    for receiver, response in results:
        if isinstance(response, Exception):  # pragma: no cover
            log.error(response, exc_info=(type(response), response, response.__traceback__))


@shared_task(bind=False, max_retries=0, queue="clock", trail=False)
def raise_exception():
    """
    Sole purpose of this task is to raise error.
    This is here to help test error handling of the this website.
    """
    raise Exception(u"Celery async task error ążśźęćńół")
