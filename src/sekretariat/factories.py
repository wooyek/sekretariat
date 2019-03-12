# coding=utf-8
import factory
import faker

from website.misc.factories import UserFactory
from . import models

fake = faker.Faker()


class SampleModelFactory(factory.DjangoModelFactory):
    name = factory.Faker('name')
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = models.SampleModel
