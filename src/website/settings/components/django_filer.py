import logging

from . import core

log = logging.getLogger(__name__)

# https://django-filer.readthedocs.io/en/latest/installation.html

core.INSTALLED_APPS += (
    'easy_thumbnails',
    'filer',
    'mptt',
)

THUMBNAIL_HIGH_RESOLUTION = True

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    # 'easy_thumbnails.processors.scale_and_crop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)

FILER_CANONICAL_URL = 'sharing/'
