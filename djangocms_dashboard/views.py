from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from cms.apphook_pool import apphook_pool
from cms.models.pagemodel import Page
from cms.models.pluginmodel import CMSPlugin
from cms.plugin_pool import plugin_pool

try:
    from django.core.urlresolvers import reverse
except ImportError:
    from django.urls import reverse

# TODO Reestruturar os codigos em classes.
# class PluginsList(DetailView):
#
#     def get_queryset(self):
#         return plugin_pool.get_all_plugins()
#
# plugins_list = PluginsList.as_view()


@login_required(login_url='')
def home(request):
    return render(request, 'djangocms_dashboard/home.html')


@login_required()
def plugins_list(request):
    context = {}
    plugin_classes = plugin_pool.get_all_plugins()
    context['plugins_info'] = []
    for plugin_class in plugin_classes:
        plugin_info = {}
        plugin_info['name'] = unicode(plugin_class.name)
        plugin_info['type'] = unicode(plugin_class.__name__)
        plugin_info['amount_published'] = CMSPlugin.objects.filter(plugin_type=plugin_info['type'],
                                                                   placeholder__page__publisher_is_draft=False).count()
        plugin_info['amount_draft'] = CMSPlugin.objects.filter(plugin_type=plugin_info['type'],
                                                               placeholder__page__publisher_is_draft=True).count()
        plugin_info['amount'] = CMSPlugin.objects.filter(plugin_type=plugin_info['type']).count()
        plugin_info['url'] = reverse('plugin_detail', kwargs={'plugin_type': plugin_info['type']})
        context['plugins_info'].append(plugin_info)

    return render(request, 'djangocms_dashboard/plugins_list.html', context)


@login_required()
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
                'title': i.page.get_title() if i.page else 'Placeholder Field',
                'url': u'/' + i.page.get_path() if i.page else '',
                'placeholder_label': i.placeholder.get_label(),
                'placeholder_static': i.placeholder.is_static,
                'not_published': i.page.publisher_is_draft if i.page else '',
                'delete_url': u'/admin/cms/page/delete-plugin/' + unicode(i.pk),
                'edit_url': u'/admin/cms/page/edit-plugin/' + unicode(i.pk),
            })
    # pages = [_.]

    return render(request, 'djangocms_dashboard/plugin_detail.html', context)


@login_required()
def apphooks_list(request):
    context = {}
    apphook_tuples = apphook_pool.get_apphooks()
    context['apphooks_info'] = []
    for apphook_tuple in apphook_tuples:
        apphook_info = {}
        apphook_info['name'] = unicode(apphook_tuple[1])
        apphook_info['class'] = unicode(apphook_tuple[0])
        apphook_info['amount'] = Page.objects.filter(application_urls=apphook_tuple[0], publisher_is_draft=False).count()
        apphook_info['url'] = reverse('apphook_detail', kwargs={'apphook_class': apphook_info['class']})

        context['apphooks_info'].append(apphook_info)


    return render(request, 'djangocms_dashboard/apphooks_list.html', context)


@login_required()
def get_apphook_class_name(apphook_obj):
    return type(apphook_obj).__name__


@login_required()
def apphook_detail(request, apphook_class):
    context = {}
    pages = Page.objects.filter(application_urls=apphook_class, publisher_is_draft=False)
    context['class'] = apphook_class
    context['amount'] = pages.count()
    context['instances'] = []

    if pages:
        for page in pages:
            context['instances'].append({
                'title': page.get_title(),
                'url': u'/' + page.get_path(),
                'not_published': page.publisher_is_draft
            })

    return render(request, 'djangocms_dashboard/apphook_detail.html', context)
