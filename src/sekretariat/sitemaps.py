import logging

from django.contrib.sitemaps import GenericSitemap

log = logging.getLogger(__name__)

items = (
    # models.?,
)


class ModelSiteMap(GenericSitemap):

    def location(self, obj):
        return obj.get_absolute_url()

    def lastmod(self, item):
        return item.publication_date


sitemaps = {item.__name__: ModelSiteMap({'queryset': item.get_published()}) for item in items}
