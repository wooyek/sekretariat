# coding=utf-8
# Copyright (c) 2018 Janusz Skonieczny


import logging

from google.oauth2 import service_account

from . import core

log = logging.getLogger(__name__)

core.INSTALLED_APPS += (
    'storages',
)

DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'

# Create new service account here:
# https://console.cloud.google.com/apis/credentials/serviceaccountkey
# See the documentation here:
# https://cloud.google.com/storage/docs/authentication#service_accounts
# You'll need to copy project_id, private_key_id, private_key and client_email from generated json file.

GS_PROJECT_ID = core.env('GOOGLE_STORAGE_ID')
GS_CREDENTIALS = service_account.Credentials.from_service_account_info({
    'token_uri': 'https://accounts.google.com/o/oauth2/token',
    'client_email': core.env('GOOGLE_STORAGE_USER'),
    'private_key_id': core.env('GOOGLE_STORAGE_KEY_ID'),
    'private_key': core.env('GOOGLE_STORAGE_KEY', lambda s: bytes(s, 'UTF-8').decode('unicode_escape')),
})
GS_BUCKET_NAME = core.env('GOOGLE_STORAGE_BUCKET')

# https://github.com/jschneier/django-storages/pull/412
# Setting this to true needs a storage.buckets.get permission
# https://cloud.google.com/storage/docs/access-control/iam-roles
GS_ALWAYS_GET_BUCKET = False
