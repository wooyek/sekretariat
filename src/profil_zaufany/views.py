# coding=utf-8
# Copyright (c) 2018 Janusz Skonieczny

import logging

from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import TemplateView
from onelogin.saml2.authn_request import OneLogin_Saml2_Authn_Request
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from social_django.utils import load_backend, load_strategy

log = logging.getLogger(__name__)


def saml_metadata_view(request):
    complete_url = reverse('social:complete', args=("saml",))
    saml_backend = load_backend(
        load_strategy(request),
        "saml",
        redirect_uri=complete_url,
    )
    metadata, errors = saml_backend.generate_metadata_xml()
    log.debug("errors: %s", errors)
    if not errors:
        return HttpResponse(content=metadata, content_type='text/xml')


class PzLoginForm(TemplateView):
    template_name = "pz_login.html"

    def get_context_data(self, **kwargs):
        complete_url = reverse('social:complete', args=("saml",))
        saml_backend = load_backend(
            load_strategy(self.request),
            "saml",
            redirect_uri=complete_url,
        )
        idp = saml_backend.get_idp('pzgovpl')
        config = saml_backend.generate_saml_config(idp)
        saml_settings = OneLogin_Saml2_Settings(
            config,
            sp_validation_only=True
        )
        log.debug("saml_settings: %s", saml_settings)
        # saml_settings = OneLogin_Saml2_Settings(custom_base_path=settings.SAML_FOLDER)
        kwargs['SAMLRequest'] = OneLogin_Saml2_Authn_Request(saml_settings).get_request()
        return super().get_context_data(**kwargs)
