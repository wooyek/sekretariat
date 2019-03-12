# coding=utf-8
# Copyright (c) 2018 Janusz Skonieczny

from . import core

core.INSTALLED_APPS += ('django_email_queue.apps.DjangoEmailQueueConfig',)
core.EMAIL_BACKEND = 'django_email_queue.backends.EmailBackend'
EMAIL_QUEUE_EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_QUEUE_EAGER = core.env("EMAIL_QUEUE_EAGER", default=False, cast=bool)
EMAIL_QUEUE_SLEEP_TIME = core.env("EMAIL_QUEUE_SLEEP_TIME", default=15, cast=int)
EMAIL_QUEUE_DISCARD_HOURS = core.env("EMAIL_QUEUE_DISCARD_HOURS", default=24, cast=int)
