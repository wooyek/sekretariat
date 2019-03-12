# coding=utf-8

from django.conf.locale.en.formats import DATETIME_INPUT_FORMATS

DATETIME_INPUT_FORMATS = [
    "%m/%d/%Y %I:%M %p",    # Moment default L LT format
] + DATETIME_INPUT_FORMATS
