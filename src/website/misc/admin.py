# coding=utf-8
# Copyright 2015 Brave Labs sp. z o.o.
# All rights reserved.
#
# This source code and all resulting intermediate files are CONFIDENTIAL and
# PROPRIETY TRADE SECRETS of Brave Labs sp. z o.o.
# Use is subject to license terms. See NOTICE file of this project for details.
from functools import reduce

from django.contrib import messages
from django.utils.translation import ugettext_lazy as _


class DynamicLookupMixin(object):
    """
    a mixin to add dynamic callable attributes like 'book__author' which
    return a function that return the instance.book.author value
    """

    def __getattr__(self, attr):
        if '__' in attr and not attr.startswith('_') and not attr.endswith('_boolean') and not attr.endswith('_short_description'):
            def dyn_lookup(instance):
                # traverse all __ lookups
                return reduce(lambda parent, child: getattr(parent, child) if parent else None, attr.split('__'), instance)

            # get admin_order_field, boolean and short_description
            dyn_lookup.admin_order_field = attr
            dyn_lookup.boolean = getattr(self, '{}_boolean'.format(attr), False)
            dyn_lookup.short_description = getattr(
                self, '{}_short_description'.format(attr),
                attr.replace('_', ' ').capitalize())

            return dyn_lookup

        # not dynamic lookup, default behaviour
        return self.__getattribute__(attr)


def save_models(modeladmin, request, queryset):
    for o in queryset:
        o.save()
    messages.info(request, "{} where saved".format(queryset.count()))


save_models.short_description = _("Save models to update auto fields")
