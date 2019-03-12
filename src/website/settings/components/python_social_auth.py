# coding=utf-8
# Copyright 2015 Brave Labs sp. z o.o.
# All rights reserved.
#
# This source code and all resulting intermediate files are CONFIDENTIAL and
# PROPRIETY TRADE SECRETS of Brave Labs sp. z o.o.
# Use is subject to license terms. See NOTICE file of this project for details.

import logging

from . import core

log = logging.getLogger(__name__)

core.INSTALLED_APPS += (
    'social_django',
)

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.twitter.TwitterOAuth',
    'social_core.backends.linkedin.LinkedinOAuth2',
    'social_core.backends.github.GithubOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.stackoverflow.StackoverflowOAuth2',
)
AUTHENTICATION_BACKENDS += core.AUTHENTICATION_BACKENDS

# Modify core setting is anyone else is making modifications
core.AUTHENTICATION_BACKENDS = AUTHENTICATION_BACKENDS
core.TEMPLATES[0]['OPTIONS']['context_processors'] += (
    'social_django.context_processors.backends',
    'social_django.context_processors.login_redirect',
)

core.MIDDLEWARE += (
    'social_django.middleware.SocialAuthExceptionMiddleware',
)

SOCIAL_AUTH_AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.twitter.TwitterOAuth',
    'social_core.backends.linkedin.LinkedinOAuth2',
    'social_core.backends.github.e91b58ee4334d2ef34ba',
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.stackoverflow.StackoverflowOAuth2',
)

SOCIAL_AUTH_SLUGIFY_USERNAMES = True
SOCIAL_AUTH_FIELDS_STORED_IN_SESSION = ['wizard', ]

# http://psa.matiasaguirre.net/docs/pipeline.html#authentication-pipeline
SOCIAL_AUTH_PIPELINE = (

    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. On some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    'social_core.pipeline.social_auth.social_details',

    # Get the social uid from whichever service we're authing thru. The uid is
    # the unique identifier of the given user in the provider.
    'social_core.pipeline.social_auth.social_uid',

    # Verifies that the current auth process is valid within the current
    # project, this is were emails and domains whitelists are applied (if
    # defined).
    'social_core.pipeline.social_auth.auth_allowed',

    # Checks if the current social-account is already associated in the site.
    # 'social_core.pipeline.social_auth.social_user',
    'introduce.pipeline.social_user',

    # 'introduce.pipeline.load_extra_data',
    'introduce.pipeline.registration_wizard',

    # Make up a username for this person, appends a random string at the end if
    # there's any collision.
    # 'social.pipeline.user.get_username',

    # Send a validation email to the user to verify its email address.
    # Disabled by default.
    # 'social.pipeline.mail.mail_validation',

    # Associates the current social details with another user account with
    # a similar email address. Disabled by default.
    # 'social.pipeline.social_auth.associate_by_email',
    # 'introduce.pipeline.force_login_for_existing_email',

    # Create a user account if we haven't found one yet.
    # 'social.pipeline.user.create_user',

    # Create the record that associated the social account with this user.
    'social_core.pipeline.social_auth.associate_user',

    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    'social_core.pipeline.social_auth.load_extra_data',

    # Update the user record with any changed info from the auth service.
    'social_core.pipeline.user.user_details',
)

SOCIAL_AUTH_STACKOVERFLOW_EXTRA_DATA = ["access_token"]
SOCIAL_AUTH_LOGIN_ERROR_URL = "/accounts/social/login-error"
SOCIAL_AUTH_RAISE_EXCEPTIONS = core.env("SOCIAL_AUTH_RAISE_EXCEPTIONS", default=False)

# https://developers.facebook.com/apps/
SOCIAL_AUTH_FACEBOOK_KEY = core.env("SOCIAL_AUTH_FACEBOOK_KEY")
SOCIAL_AUTH_FACEBOOK_SECRET = core.env("SOCIAL_AUTH_FACEBOOK_SECRET")

# https://apps.twitter.com/app/new
SOCIAL_AUTH_TWITTER_KEY = core.env("SOCIAL_AUTH_TWITTER_KEY")
SOCIAL_AUTH_TWITTER_SECRET = core.env("SOCIAL_AUTH_TWITTER_SECRET")

# https://console.developers.google.com/project
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = core.env("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = core.env("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET")

# https://github.com/settings/applications/new
SOCIAL_AUTH_GITHUB_KEY = core.env("SOCIAL_AUTH_GITHUB_KEY")
SOCIAL_AUTH_GITHUB_SECRET = core.env("SOCIAL_AUTH_GITHUB_SECRET")

# https://www.linkedin.com/developer/apps/new
SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY = core.env("SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY")
SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET = core.env("SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET")

# http://stackapps.com/apps/oauth/register
SOCIAL_AUTH_STACKOVERFLOW_KEY = core.env("SOCIAL_AUTH_STACKOVERFLOW_KEY", int)
SOCIAL_AUTH_STACKOVERFLOW_API_KEY = core.env("SOCIAL_AUTH_STACKOVERFLOW_API_KEY")
SOCIAL_AUTH_STACKOVERFLOW_SECRET = core.env("SOCIAL_AUTH_STACKOVERFLOW_SECRET")
