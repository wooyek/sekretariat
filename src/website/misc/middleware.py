# coding=utf-8
# Copyright 2018 Janusz Skonieczny
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.views.defaults import server_error


class XHeadersMiddleware(MiddlewareMixin):
    """
    Adds additional headers to the respose.

    X-Current-Location - for detecting redirects with XMLHTTPRequest.
    Inspired by django.core.xhreaders.populate_xheaders
    """

    def process_response(self, request, response):
        response['X-Current-Location'] = request.path
        return response


class ProcessErrorsMiddleware(object):  # pragma: no cover
    def process_exception(self, request, exception):
        if settings.DEBUG:
            return
        template_name = '500_ajax.html' if request.is_ajax else "500.html"
        return server_error(request, template_name=template_name, exception=exception)
