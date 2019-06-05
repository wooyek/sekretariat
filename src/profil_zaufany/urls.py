# -*- coding: utf-8 -*-
from django.urls import path

from . import views as v

app_name = 'profil_zaufany'

urlpatterns = [
    path('meta', v.saml_metadata_view, name='saml_metadata_view'),
    path('', v.PzLoginForm.as_view(), name='PzLoginForm'),
]
