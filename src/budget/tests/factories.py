# coding=utf-8
from decimal import Decimal

import factory
import faker

from website.misc.factories import UserFactory
from .. import models

fake = faker.Faker()


class AccountGroupFactory(factory.DjangoModelFactory):
    name = factory.Faker('catch_phrase')
    number = factory.Sequence(lambda n: n)

    class Meta:
        model = models.AccountGroup


class AccountFactory(factory.DjangoModelFactory):
    name = factory.Faker('catch_phrase')
    number = factory.Sequence(lambda n: n)
    group = factory.SubFactory(AccountGroupFactory)

    class Meta:
        model = models.Account


class BudgetFactory(factory.DjangoModelFactory):
    amount = Decimal('123')
    account = factory.SubFactory(AccountFactory)
    year = 2012
    month = 5

    class Meta:
        model = models.Budget


class ApplicationFactory(factory.DjangoModelFactory):
    date = factory.Faker('future_date', end_date="+30d")
    amount = Decimal('13')
    requester = factory.SubFactory(UserFactory)
    title = factory.Faker('catch_phrase')
    description = factory.Faker('catch_phrase')
    manager = factory.SubFactory(UserFactory)

    class Meta:
        model = models.Application
