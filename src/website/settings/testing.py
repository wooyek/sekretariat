# coding=utf-8

"""
These should mimic a production settings making minimal modifications to accommodate tests
"""

import logging
import os
import sys
from pathlib import Path

import environ

logging.basicConfig(format='%(asctime)s %(levelname)-7s %(thread)-5d %(filename)s:%(lineno)s | %(funcName)s | %(message)s', datefmt='%H:%M:%S')
logging.getLogger().setLevel(logging.DEBUG)
logging.disable(logging.NOTSET)
logging.getLogger('environ').setLevel(logging.INFO)

logging.debug("Settings loading: %s" % __file__)

name = __name__.split('.')[-1].upper()
print("""
╭─────────{border}──────────╮
│ Loading {name} settings │
╰─────────{border}──────────╯
""".format(name=name, border='─' * len(name)), file=sys.stderr)

# Set defaults for when env file is not present.
# These need to be entered into an environment,
# for django settings (or anything else) to load it from there
# It may or may not be overridden by read_env below.
os.environ.update(
    DEBUG='False',
    ASSETS_DEBUG='False',
)

# This will read missing environment variables from a file
# We want to do this before loading any base settings as they may depend on environment
environment_config = Path(__file__).with_suffix('.env')
if environment_config.exists():
    environ.Env.read_env(str(environment_config))

if 'DATABASE_URL' not in os.environ:
    # This a default fallback for local development and testing
    BASE_DIR = Path(__file__).parents[3]
    os.environ['DATABASE_URL'] = 'sqlite://' + str(BASE_DIR / 'data' / 'db.dev.sqlite3')
    os.environ['DATABASE_TEST_NAME'] = 'sqlite://' + str(BASE_DIR / 'data' / 'db.test.sqlite3')

# noinspection PyUnresolvedReferences
from .base import *  # noqa: F402, F403, F401 isort:skip

# https://docs.djangoproject.com/en/dev/topics/email/#console-backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
LOGGING['handlers']['mail_admins']['email_backend'] = 'django.core.mail.backends.dummy.EmailBackend'  # noqa: F405

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# The name of the class to use to run the test suite
TEST_RUNNER = 'website.misc.testing.KeepDbTestRunner'

CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
TASKER_ALWAYS_EAGER = True
