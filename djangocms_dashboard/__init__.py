from __future__ import absolute_import, unicode_literals

import django

__all__ = ['VERSION']


try:
    import pkg_resources
    VERSION = pkg_resources.get_distribution('djangocms-dashboard').version
except Exception:
    VERSION = 'unknown'


# Code that discovers files or modules in INSTALLED_APPS imports this module.

urls = ('djangocms_dashboard',)

default_app_config = 'djangocms_dashboard.apps.DjangoCmsDashboardConfig'
