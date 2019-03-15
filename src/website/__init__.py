# coding=utf-8
"""Website configuration and shared commons package for Sekretariat."""

__author__ = """Janusz Skonieczny"""
__email__ = 'js+pypi@bravelabs.pl'
__copyright__ = "Copyright 2018, Janusz Skonieczny"
__maintainer__ = """Janusz Skonieczny"""
__credits__ = ["""Janusz Skonieczny"""]
__version__ = '0.1.2'
__status__ = "Alpha"
__license__ = "Proprietary"
__date__ = '2019-03-15 22:19'


def get_strict_version():
    from distutils.version import StrictVersion
    return StrictVersion(__version__)
