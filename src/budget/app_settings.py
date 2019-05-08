# coding=utf-8

from django.conf import settings

# This is an example
from environ import environ

BUDGET_SECRET = settings.SECRET_KEY[::4]

env = environ.Env()

BUDGET_TEAM_DOMAIN = env("BUDGET_TEAM_DOMAIN", default='pspo.edu.pl')
BUDGET_TEAM_GROUP = env("BUDGET_TEAM_GROUP", default='Team')
BUDGET_ACCOUNTANTS_GROUP = env("BUDGET_ACCOUNTANTS_GROUP", default='Accountants')
BUDGET_MANAGERS_GROUP = env("BUDGET_MANAGERS_GROUP", default='Managers')
BUDGET_CONTROL_GROUP = env("BUDGET_MANAGERS_GROUP", default='Control')
