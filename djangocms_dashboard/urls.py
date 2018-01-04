from django.conf.urls import url
from decorate_url import decorated_url
from django.contrib.auth.decorators import login_required


urlpatterns = [
    url(r'^$', 'djangocms_dashboard.views.home', name='home'),
    decorated_url(r'^plugins/$', 'djangocms_dashboard.views.plugins_list', name='plugins_list', wrap=login_required),
    decorated_url(r'^apphooks/$', 'djangocms_dashboard.views.apphooks_list', name='apphooks_list', wrap=login_required),
    # url(r'^$', plugins_list),
    decorated_url(r'^plugin_detail/(?P<plugin_type>\w+)$', 'djangocms_dashboard.views.plugin_detail', name='plugin_detail', wrap=login_required),
    decorated_url(r'^apphook_detail/(?P<apphook_class>\w+)$', 'djangocms_dashboard.views.apphook_detail', name='apphook_detail', wrap=login_required)
]
