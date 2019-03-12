# -*- coding: utf-8 -*-

"""Console script for multiinfo."""
import logging
import os

import click
import click_log
from environ import environ

log = logging.getLogger(__name__)
click_log.basic_config(log)


@click.group()
@click.option('-s', '--settings', type=click.Path(), help="File with configuration settings")
@click_log.simple_verbosity_option(logging.getLogger())
def main(settings):
    """Website CLI"""
    logging.basicConfig(
        format='%(asctime)s %(levelname)-7s %(thread)-5d %(filename)s:%(lineno)s | %(funcName)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    if settings:
        environ.Env.read_env(settings)
    setup_django()


@main.command()
@click.argument('name', nargs=-1, required=True)
def hello(name):
    """Pull contact data and create contacts for given delivery no"""
    try:
        log.info("Hello! %s", name)
    except Exception as ex:
        log.error("", exc_info=ex)
        raise


def setup_django():  # pragma: no cover
    DJANGO_SETTINGS_MODULE = os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")
    log.info("DJANGO_SETTINGS_MODULE=%s", DJANGO_SETTINGS_MODULE)
    import django
    django.setup()


if __name__ == "__main__":  # pragma: no cover
    main()
