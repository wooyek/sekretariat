# coding=utf-8
# sitemaps.py

from django.contrib import sitemaps
from django.urls import reverse

import sekretariat.sitemaps


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return [
            # 'privacy', 'tos',
        ]

    def location(self, item):
        return reverse(item)


sitemaps = sekretariat.sitemaps.sitemaps
