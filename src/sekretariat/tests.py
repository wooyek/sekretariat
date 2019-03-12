# coding=utf-8

import logging

import faker
from django import test
from django.shortcuts import resolve_url

from website.misc.testing import UserTestCase
from . import factories, models

log = logging.getLogger(__name__)
fake = faker.Faker()


class SampleDetailTests(UserTestCase):
    def test_anonymous(self):
        item = factories.SampleModelFactory()
        url = resolve_url("sekretariat:SampleDetail", item.pk)
        response = test.Client().get(url)
        self.assertEqual(302, response.status_code)

    def test_forbidden(self):
        item = factories.SampleModelFactory()
        url = resolve_url('sekretariat:SampleDetail', item.pk)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

    def test_get(self):
        item = factories.SampleModelFactory(user=self.user)
        url = resolve_url('sekretariat:SampleDetail', item.pk)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)


class SampleCreateTests(UserTestCase):
    def test_anonymous(self):
        url = resolve_url('sekretariat:SampleCreate')
        response = test.Client().get(url)
        self.assertEqual(302, response.status_code)

    def test_get(self):
        url = resolve_url('sekretariat:SampleCreate')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_post(self):
        url = resolve_url('sekretariat:SampleCreate')
        response = self.client.post(url, data={
            'user': self.user.pk
        })
        item = models.SampleModel.objects.first()
        self.assertRedirects(response, resolve_url('sekretariat:SampleDetail', item.pk), fetch_redirect_response=False)
