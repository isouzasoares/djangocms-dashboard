from django.conf.urls import url
# from .views import plugins_list

urlpatterns = [
    url(r'^$', 'djangocms_dashboard.views.home', name='home'),
    url(r'^apphooks$', 'djangocms_dashboard.views.apphooks_list', name='apphooks_list'),
    # url(r'^$', plugins_list),
    url(r'^plugin_detail/(?P<plugin_type>\w+)$', 'djangocms_dashboard.views.plugin_detail', name='plugin_detail'),
    url(r'^apphook_detail/(?P<apphook_class>\w+)$', 'djangocms_dashboard.views.apphook_detail', name='apphook_detail')
]
