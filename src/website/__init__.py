# coding=utf-8
"""Website configuration and shared commons package for Sekretariat."""

__author__ = """Janusz Skonieczny"""
__email__ = 'js+pypi@bravelabs.pl'
__copyright__ = "Copyright 2018, Janusz Skonieczny"
__maintainer__ = """Janusz Skonieczny"""
__credits__ = ["""Janusz Skonieczny"""]
__version__ = '0.1.71'
__status__ = "Alpha"
__license__ = "Proprietary"
__date__ = '2019-10-30 10:28'


def get_strict_version():
    from distutils.version import StrictVersion
    return StrictVersion(__version__)
