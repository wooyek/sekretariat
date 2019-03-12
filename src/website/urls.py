"""Pelikan website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
"""
from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.views.i18n import JavaScriptCatalog
from django_error_views.handlers import *  # noqa F401

from .admin import custom_admin_site
from .misc import debug
from .sitemaps import sitemaps
sitemaps = {}

urlpatterns = [
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', include('smuggler.urls')),  # before admin url patterns!
    path('admin/', custom_admin_site.urls),
    path('err/', debug.ErrView.as_view(), name='err'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/password_reset/', auth_views.PasswordResetView.as_view(), name='admin_password_reset'),
    path('unsubscribe/', include(django_opt_out.urls)),
    path('', include('sekretariat.urls')),
]

urlpatterns = i18n_patterns(*urlpatterns)

if 'debug_toolbar' in settings.INSTALLED_APPS:
    if settings.DEBUG or 'SHOW_TOOLBAR_CALLBACK' in settings.DEBUG_TOOLBAR_CONFIG:
        import debug_toolbar  # noqa: F402

        urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
        ]

if settings.MEDIA_SERVED:
    from django.views.static import serve

    urlpatterns += [
        path('media/<path:path>', serve, kwargs={'document_root': settings.MEDIA_ROOT}),
    ]
