# coding=utf-8
# Copyright (c) 2018 Janusz Skonieczny

import logging

from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext_lazy

log = logging.getLogger(__name__)

# Text to put at the end of each page's <title>.
admin.site.site_title = settings.ADMIN_SITE_TITLE or ugettext_lazy('Django site admin')

# Text to put in each page's <h1>.
admin.site.site_header = settings.ADMIN_SITE_HEADER or ugettext_lazy('Django administration')

# Text to put at the top of the admin index page.
admin.site.index_title = settings.ADMIN_INDEX_TITLE or ugettext_lazy('Site administration')

# Renamed proxy will make things easy if we would want to customize things further.
custom_admin_site = admin.site
