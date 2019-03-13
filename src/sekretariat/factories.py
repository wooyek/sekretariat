# coding=utf-8
import factory
import faker
from django.utils import timezone

from . import models

fake = faker.Faker()


class OpenOfficeGroupFactory(factory.DjangoModelFactory):
    name = factory.Faker('catch_phrase')

    class Meta:
        model = models.OpenOfficeGroup


class OpenOfficeSlotFactory(factory.DjangoModelFactory):
    group = factory.SubFactory(OpenOfficeGroupFactory)
    start = factory.Faker('future_datetime', end_date='+7d', tzinfo=timezone.get_current_timezone())

    class Meta:
        model = models.OpenOfficeSlot
