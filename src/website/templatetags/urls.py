# coding=utf-8
# Copyright (c) 2018 Janusz Skonieczny

import logging
from collections import OrderedDict
from urllib.parse import parse_qsl, urlencode

from django import template

log = logging.getLogger(__name__)
register = template.Library()


@register.simple_tag(takes_context=True)
def append_get(context, **kwargs):
    url = context['request'].get_full_path()
    logging.debug("path: %s" % url)
    if "?" in url:
        path, qs = url.split("?")
        query_params = OrderedDict(parse_qsl(qs))
        logging.debug("query_params: %s" % query_params)
        query_params.update(kwargs)
        logging.debug("query_params: %s" % query_params)
        return path + "?" + urlencode(query_params, doseq=True)
    else:
        suffix = urlencode(kwargs)
        return url + "?" + suffix
