# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.views.generic import TemplateView

from . import views as v

app_name = 'sekretariat'

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name="sekretariat/base.html")),
    url(r'^sample/create', v.SampleCreate.as_view(), name='SampleCreate'),
    url(r'^sample/(?P<pk>[\d]+)/', v.SampleDetail.as_view(), name='SampleDetail'),
]
