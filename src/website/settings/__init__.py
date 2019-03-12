from __future__ import absolute_import

import logging
import os
import sys

# Loading here any other settings is possibly a destructive operation
# as purposed settings modules can modify sys.environment
# leading to setting up configuration variables that should remain empty

if os.environ.get("DJANGO_SETTINGS_MODULE", None) == "website.settings":
    # We'll try to guess settings module when DJANGO_SETTINGS_MODULE to default (this module)
    # It's unusable as it is, we may as well try to correct this.
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        logging.info("Module website.settings is loading testing settings. Set DJANGO_SETTINGS_MODULE to override this.")
        from .testing import *  # noqa: F401, F403
    else:  # pragma: no cover
        logging.info("Module website.settings is loading development settings. Set DJANGO_SETTINGS_MODULE to override this.")
        from .development import *  # noqa: F401, F403
