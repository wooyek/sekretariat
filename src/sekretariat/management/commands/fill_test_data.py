# coding=utf-8
import logging

from django.core.management.base import BaseCommand

from ... import models

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fill database with random test data'

    def add_arguments(self, parser):  # noqa
        parser.add_argument('--force', action='store_true', dest='force', default=False, help='May overwrite existing data')
        parser.add_argument('--on-empty', action='store_true', dest='on_empty', default=False, help='Only if database is emtpy')
        parser.add_argument('--count', action=None, dest='count', default=50, help='Number of destinations')

    def handle(self, count=None, *args, **options):
        if not self.accept_state(**options):
            return  # noqa
        logging.info("Faking test data: %s", count)
        from sekretariat import factories
        items = factories.OpenOfficeSlotFactory.create_batch(int(count))
        log.info("Created: %s", items)

    # noinspection PyUnusedLocal
    @staticmethod
    def accept_state(force=False, on_empty=True, **kwargs):
        if force:
            return True
        try:
            assert models.OpenOfficeSlot.objects.count() == 0
            return True
        except AssertionError as ex:
            if on_empty:
                log.info("Ignoring fake data generation, database is not empty.")
                return False
            raise ex
