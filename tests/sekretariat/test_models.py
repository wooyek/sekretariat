#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase

from sekretariat import models


class TestSampleModel(TestCase):

    def test_something(self):
        self.assertIsNotNone(models)
