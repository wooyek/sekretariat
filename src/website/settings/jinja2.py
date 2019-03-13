# coding=utf-8
# Copyright 2015 Brave Labs sp. z o.o.
# All rights reserved.
#
# This source code and all resulting intermediate files are CONFIDENTIAL and
# PROPRIETY TRADE SECRETS of Brave Labs sp. z o.o.
# Use is subject to license terms. See NOTICE file of this project for details.

from datetime import date, datetime

from babel.support import Translations
from dinja2.filters import do_append_get, do_class_name
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.shortcuts import resolve_url
from django.templatetags.i18n import GetLanguageInfoListNode
from django.utils import translation
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _
from django_assets.env import get_env
from django_assets.templatetags import assets
from django_babel.templatetags import babel
# from gargoyle import gargoyle
from jinja2 import Environment

# from avatars import get_avatar_url


def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': url,
        'assets': assets,
        # 'gravatar_url': get_avatar_url,
        'get_current_language': get_language,
        'get_available_languages': get_available_languages,
        'get_language_info_list': get_language_info_list,
        # 'switch': gargoyle.is_active,
    })

    env.filters.update(
        datetimeformat=babel.datetimefmt,
        dateformat=babel.datefmt,
        timeformat=babel.timefmt,
        natural_period=natural_period,
        # timedeltaformat=format_timedelta,

        numberformat=babel.numberfmt,
        decimalformat=babel.decimalfmt,
        currencyformat=babel.currencyfmt,
        percentformat=babel.percentfmt,
        scientificformat=babel.scientificfmt,
        append_get=do_append_get,
        class_name=do_class_name,
    )

    env.add_extension('jinja2.ext.loopcontrols')
    env.add_extension('jinja2.ext.with_')
    env.add_extension('dinja2.ext.active')
    # from ext.relative_templates import RelativeInclude
    # env.add_extension(RelativeInclude)

    # env.add_extension('jinja2_highlight.HighlightExtension')
    # env.add_extension('jinja2htmlcompress.HTMLCompress')
    env.add_extension('webassets.ext.jinja2.AssetsExtension')
    env.assets_environment = get_env()

    env.add_extension('jinja2.ext.i18n')

    if settings.USE_I18N:
        from django.utils import translation
        env.install_gettext_translations(translation, newstyle=True)
    else:  # pragma: no cover
        env.install_null_translations(newstyle=True)
    return env


def get_translations():  # pragma: no cover
    from django.conf import settings
    # take only locale codes and discard locale names
    # languages = next(zip(*settings.LANGUAGES))
    languages = get_language()
    dirname = settings.LOCALE_PATHS[0]
    translations = Translations.load(dirname, locales=languages, domain='django')
    return translations


def url(viewname, *args, **kwargs):
    # TODO: automatycznie tutaj ustawiać bierzący namespace
    return resolve_url(viewname, *args, **kwargs)


def get_available_languages():  # pragma: no cover
    return [(k, translation.ugettext(v)) for k, v in settings.LANGUAGES]


def get_language_info_list(langs):  # pragma: no cover
    helper = GetLanguageInfoListNode(None, None)
    return [helper.get_language_info(lang) for lang in langs]


def natural_period(value, arg=None):
    """
    For date values that are tomorrow, today or yesterday compared to
    present day returns representing string. Otherwise, returns a string
    formatted according to settings.DATE_FORMAT.
    """
    try:
        tzinfo = getattr(value, 'tzinfo', None)
        value = date(value.year, value.month, value.day)
    except AttributeError:
        # Passed value wasn't a date object
        return value
    except ValueError:
        # Date arguments out of range
        return value
    today = datetime.now(tzinfo).date()
    delta = value - today
    if delta.days == 0:
        return _('today')
    elif delta.days == 1:
        return _('tomorrow')
    elif delta.days == -1:
        return _('yesterday')
    elif delta.days > -7:
        return _('this week')
    return babel.datetimefmt(value, arg)
