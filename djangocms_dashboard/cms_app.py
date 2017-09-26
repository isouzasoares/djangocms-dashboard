# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool


class DashboardCMSApphook(CMSApp):
    app_name = 'djangocms_dashboard_test'
    urls = ['urls']
    name = 'DjangoCMS Dashboard'

    def get_urls(self, page=None, language=None, **kwargs):
        return ["urls"]


apphook_pool.register(DashboardCMSApphook)