# coding=utf-8
# Copyright (c) 2018 Janusz Skonieczny


from . import core

core.INSTALLED_APPS += ('django_opt_out.apps.DjangoOptOutConfig',)
OPT_OUT_SECRET = 'a6715955-c422-4c02-83de-13eef03f6e50'
