from django.conf.urls import url

urlpatterns = [
    url(r'^$', 'djangocms_dashboard.views.home', name='home'),
    url(r'^plugins/$', 'djangocms_dashboard.views.plugins_list', name='plugins_list'),
    url(r'^apphooks/$', 'djangocms_dashboard.views.apphooks_list', name='apphooks_list'),
    # url(r'^$', plugins_list),
    url(r'^plugin_detail/(?P<plugin_type>\w+)$', 'djangocms_dashboard.views.plugin_detail', name='plugin_detail'),
    url(r'^apphook_detail/(?P<apphook_class>\w+)$', 'djangocms_dashboard.views.apphook_detail', name='apphook_detail'),
    # url(r'^plugins/$', 'djangocms_dashboard.views.plugins_list.some_view', name='some_view'),
    # url(r'^plugins/export/csv/$', 'djangocms_dashboard.views.plugins_list', name='export_users_csv'),
]
