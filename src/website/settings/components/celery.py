# coding=utf-8

import logging

from celery.schedules import crontab

from . import core

log = logging.getLogger(__name__)

# Celery
# http://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html#configuration

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = 'Europe/Warsaw'
CELERY_ENABLE_UTC = True
CELERY_SEND_TASK_ERROR_EMAILS = True

# http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html#crontab-schedules

CELERYBEAT_SCHEDULE = {
    'minutes': {
        'task': 'website.misc.tasks.every_minute',
        'schedule': crontab()  # Execute every minute
    },
    'hours': {
        'task': 'website.misc.tasks.every_hour',
        'schedule': crontab(minute=0)  # Execute every hour
    },
    'days': {
        'task': 'website.misc.tasks.every_day',
        'schedule': crontab(minute=0, hour=3)  # Execute daily at 3 in the morning
    },
    'mondays': {
        'task': 'website.misc.tasks.every_monday',
        'schedule': crontab(minute=0, hour=1, day_of_week=1)  # Execute weekly at 1 in the morning
    },
}

CELERY_QUEUES = {
    "celery": {},
    "beats": {
        "queue_arguments": {'x-message-ttl': 120000}
    },
    "default_queue": {
        "queue_arguments": {'x-message-ttl': 120000}
    },
    "clock": {
        "queue_arguments": {'x-message-ttl': 120000}
    },
}

# Sync task testing
# http://docs.celeryproject.org/en/2.5/configuration.html?highlight=celery_always_eager#celery-always-eager

CELERY_ALWAYS_EAGER = core.env('CELERY_ALWAYS_EAGER', bool, default=False)
CELERY_EAGER_PROPAGATES_EXCEPTIONS = core.env('CELERY_EAGER_PROPAGATES_EXCEPTIONS', bool, default=True)

BROKER_URL = core.env("CLOUDAMQP_URL", default=None) or core.env("BROKER_URL")
