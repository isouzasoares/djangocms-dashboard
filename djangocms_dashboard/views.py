from django.shortcuts import render
from cms.plugin_pool import plugin_pool
from cms.models.pluginmodel import CMSPlugin
try:
    from django.core.urlresolvers import reverse
except ImportError:
    from django.urls import reverse


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
    instances = CMSPlugin.objects.filter(plugin_type=plugin_type)
    if instances:
        context['amount'] = instances.count()
        context['name'] = instances.first().get_plugin_name()
        context['type'] = instances.first().plugin_type
        context['instances'] = []
        for i in instances:
            context['instances'].append({
                'title': i.page.get_title(),
                'url': u'/' + i.page.get_path(),
                'placeholder': i.placeholder.get_label(),
            })
    # pages = [_.]

    return render(request, 'djangocms_dashboard/plugin_detail.html', context)
