"""
WSGI config for website project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
"""

# Print statements may help with gunicorn debugging

print("Importing: %s" % __file__)

import logging  # noqa: F402
import os  # noqa: F402

logging.basicConfig(format='%(asctime)s %(levelname)-7s %(thread)-5d %(filename)s:%(lineno)s | %(funcName)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger().setLevel(logging.DEBUG)
logging.disable(logging.NOTSET)

logging.info('Loading %s', __name__)


DJANGO_SETTINGS_MODULE = os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")
print("DJANGO_SETTINGS_MODULE=", DJANGO_SETTINGS_MODULE)
from django.conf import settings  # noqa: F402 isort:skip

# determine where is the single absolute path that
# will be used as a reference point for other directories
SITE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
logging.debug("SITE_ROOT: %s" % SITE_ROOT)
logging.debug("settings.DEBUG: %s" % settings.DEBUG)


def setup_newrelic(app):
    # By default newrelic should be configured with env
    if 'NEW_RELIC_LICENSE_KEY' not in os.environ:
        logging.warning("Missing NEW_RELIC_LICENSE_KEY environment setting")
        return app

    import newrelic.agent  # noqa: F402 isort:skip
    from pathlib import Path  # noqa: F402 isort:skip
    newrelic.agent.initialize(str(Path(__file__).parents[2] / 'newrelic.ini'))
    return newrelic.agent.WSGIApplicationWrapper(app)


def setup_sentry(app):
    from raven.contrib.django.raven_compat.middleware.wsgi import Sentry  # noqa: F402 isort:skip
    return Sentry(app)


# def setup_white_noise(app):
#     from whitenoise.django import DjangoWhiteNoise  # noqa: F402 isort:skip
#     return DjangoWhiteNoise(app)


def setup_celery():
    # This will make sure the app is always imported when
    # Django starts so that shared_task will use this app.
    # noinspection PyUnresolvedReferences
    from website.misc.celery import app as celery_app  # noqa: F401 F403 isort:skip


# Obtain WSGIHandler
from django.core.wsgi import get_wsgi_application  # noqa: F402 isort:skip

application = get_wsgi_application()
application = setup_newrelic(application)
application = setup_sentry(application)
# application = setup_white_noise(application)

logging.debug("application: %s" % application)
