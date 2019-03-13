#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for this project `website` package."""
import pytest

import website
from sekretariat.factories import OpenOfficeSlotFactory


def test_version_exists():
    """This is a stupid test dummy validating import of website"""
    assert website.__version__


@pytest.mark.django_db
def test_home_view(client):
    """Test if a home url does actually load"""
    OpenOfficeSlotFactory()
    response = client.get('/', follow=True)
    assert 200 == response.status_code
