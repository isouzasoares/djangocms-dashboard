from __future__ import absolute_import, unicode_literals

import warnings

from django.conf import settings
from django.utils import six
from django.utils.lru_cache import lru_cache


@lru_cache()
def get_config():
    USER_CONFIG = getattr(settings, 'DEBUG_TOOLBAR_CONFIG', {})
    CONFIG = CONFIG_DEFAULTS.copy()
    CONFIG.update(USER_CONFIG)
    return CONFIG
