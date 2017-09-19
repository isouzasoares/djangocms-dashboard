from django.shortcuts import render

from cms.apphook_pool import apphook_pool
from cms.models.pagemodel import Page
from cms.models.pluginmodel import CMSPlugin
from cms.plugin_pool import plugin_pool

try:
    from django.core.urlresolvers import reverse
except ImportError:
    from django.urls import reverse


# class PluginsList(DetailView):
#
#     def get_queryset(self):
#         return plugin_pool.get_all_plugins()
#
# plugins_list = PluginsList.as_view()



def home(request):
    context = {}
    plugin_classes = plugin_pool.get_all_plugins()
    context['plugins_info'] = []
    for plugin_class in plugin_classes:
        plugin_info = {}
        plugin_info['name'] = unicode(plugin_class.name)
        plugin_info['type'] = unicode(plugin_class.__name__)
        plugin_info['amount'] = CMSPlugin.objects.filter(plugin_type=plugin_info['type']).count()
        plugin_info['url'] = reverse('plugin_detail', kwargs={'plugin_type': plugin_info['type']})
        context['plugins_info'].append(plugin_info)

    return render(request, 'djangocms_dashboard/home.html', context)


def plugin_detail(request, plugin_type):
    context = {}
    # context['name'] = plugin_name
    # context['type'] = plugin_type
    # context['amount'] = plugin_amount

    instances = CMSPlugin.objects.filter(plugin_type=plugin_type)
    if instances:
        context['amount'] = instances.count()
        context['name'] = instances.first().get_plugin_name()
        context['type'] = instances.first().plugin_type
        context['instances'] = []
        for i in instances:
    #TODO: arrumar URL (delete_url e edit_url hard coded)
            context['instances'].append({
                'title': i.page.get_title(),
                'url': u'/' + i.page.get_path(),
                'placeholder_label': i.placeholder.get_label(),
                'placeholder_static': i.placeholder.is_static,
                'not_published': i.page.publisher_is_draft,
                'delete_url': u'/admin/cms/page/delete-plugin/' + unicode(i.pk),
                'edit_url': u'/admin/cms/page/edit-plugin/' + unicode(i.pk),
            })
    # pages = [_.]

    return render(request, 'djangocms_dashboard/plugin_detail.html', context)


def apphooks_list(request):
    context = {}
    apphook_tuples = apphook_pool.get_apphooks()
    context['apphooks_info'] = []
    for apphook_tuple in apphook_tuples:
        apphook_info = {}
        apphook_info['name'] = unicode(apphook_tuple[1])
        apphook_info['class'] = unicode(apphook_tuple[0])
        # TODO alterar publisher para FALSE
        apphook_info['amount'] = Page.objects.filter(application_urls=apphook_tuple[0], publisher_is_draft=True).count()
        apphook_info['url'] = reverse('apphook_detail', kwargs={'apphook_class': apphook_info['class']})

        context['apphooks_info'].append(apphook_info)


    return render(request, 'djangocms_dashboard/apphooks_list.html', context)


def get_apphook_class_name(apphook_obj):
    return type(apphook_obj).__name__


def apphook_detail(request, apphook_class):
    context = {}
    # TODO alterar publisher para FALSE
    pages = Page.objects.filter(application_urls=apphook_class, publisher_is_draft=True)
    # TODO Pegar o nome do apphook
    context['name'] = 'Nome'
    context['class'] = apphook_class
    context['amount'] = pages.count()

    if pages:
        for page in pages:
            context['instances'].append({
                'title': page.get_title(),
                'url': u'/' + page.get_path(),
            })

    return render(request, 'djangocms_dashboard/apphook_detail.html', context)
