# coding=utf-8
# Copyright 2015 Brave Labs sp. z o.o.
# All rights reserved.
#
# This source code and all resulting intermediate files are CONFIDENTIAL and
# PROPRIETY TRADE SECRETS of Brave Labs sp. z o.o.
# Use is subject to license terms. See NOTICE file of this project for details.
import json
import logging
from smtplib import SMTPAuthenticationError, SMTPServerDisconnected

import html2text
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail as django_send_mail
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import render_to_string
from sparkpost.exceptions import SparkPostAPIException


def send_mail(template_path, ctx, to):
    """Simplifies message rendering"""

    ctx.setdefault('BASE_URL', settings.BASE_URL)

    message = render_to_string(template_path + '.jinja2', ctx)
    html_message = render_to_string(template_path + '.html', ctx)
    subject, message = message.split("\n", 1)

    if not isinstance(to, list):
        to = [to]

    django_send_mail(
        subject=subject,
        message=message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=to
    )


def send_mail_template(template, ctx, subject, to=None, **kwargs):
    """Simplifies message rendering"""

    ctx.setdefault('BASE_URL', settings.BASE_URL)

    html_message = render_to_string(template, ctx)
    try:
        text_message = render_to_string(template.replace(".html", ".jinja2"), ctx)
    except TemplateDoesNotExist:
        text_message = html2text.html2text(html_message)

    if not isinstance(to, list):
        to = [to]

    kwargs.setdefault('from_email', settings.DEFAULT_FROM_EMAIL)
    kwargs.setdefault('reply_to', [settings.DEFAULT_REPLY_TO_EMAIL])

    message = EmailMultiAlternatives(subject, body=text_message, to=to, **kwargs)
    if html_message:
        message.attach_alternative(html_message, 'text/html')
    logging.debug("to: %s", to)
    if 'unsubscribe' in ctx:
        message.extra_headers['List-Unsubscribe'] = "<{}>".format(ctx['unsubscribe'])
        message.extra_headers['X-MSYS-API'] = json.dumps({'options': {'transactional': True}})
    try:
        return message.send()
    except SparkPostAPIException as ex:
        if ex.status == 1902 or not settings.FAIL_ON_EMAIL_SUPPRESSION:
            logging.error("Email suppression: %s", to, exc_info=ex)
        else:
            raise
    except (SMTPServerDisconnected, SMTPAuthenticationError) as ex:
        logging.error("", exc_info=ex)
        # Retry once
        return message.send()
