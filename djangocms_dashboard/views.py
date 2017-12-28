from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from cms.apphook_pool import apphook_pool
from cms.models.pagemodel import Page
from cms.models.pluginmodel import CMSPlugin
from cms.plugin_pool import plugin_pool, PluginPool
from .forms import DashboardFieldsForm
from django.views.generic import DetailView, ListView
from unicodedata import normalize

try:
    from django.core.urlresolvers import reverse
except ImportError:
    from django.urls import reverse


def remover_espacos(n):
    return ' '.join(n.split())


def remover_acentos(txt):
    return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')


def limpar_nome(nome):
    sem_espacoes = remover_espacos(nome)
    return remover_acentos(sem_espacoes).lower()



# @login_required()
class PluginsList(ListView):
    template_name = 'djangocms_dashboard/plugins_list.html'
    model = CMSPlugin

    def filter_plugins(self, keyword, plugins_list, range, comparation):
        plugins_filtered = []
        for plugin in plugins_list:
            plugin.type = unicode(plugin.__name__)
            plugin.amount = CMSPlugin.objects.filter(plugin_type=plugin.type).count()
            if keyword:
                keyword = unicode(keyword)
                plugins_filtered.append(plugin) if limpar_nome(keyword) in (
                limpar_nome(plugin.name) or limpar_nome(plugin.plugin_type)) else None

            elif range and comparation:
                if 'gte' in comparation:
                    if plugin.amount > int(range):
                        plugins_filtered.append(plugin)

                elif 'lte' in comparation:
                    plugins_filtered.append(plugin) if plugin.amount < int(range) else None
                elif 'equ' in comparation:
                    plugins_filtered.append(plugin) if plugin.amount == int(range) else None
            else:
                plugins_filtered = plugins_list

        return plugins_filtered

    def get_plugins_list(self, plugins):
        plugins_to_show = []
        for plugin in plugins:
            plugin_info = {}
            plugin_info['name'] = unicode(plugin.name)
            plugin_info['type'] = unicode(plugin.__name__)
            plugin_info['amount_published'] = CMSPlugin.objects.filter(plugin_type=plugin_info['type'],
                                                                       placeholder__page__publisher_is_draft=False).count()
            plugin_info['amount'] = CMSPlugin.objects.filter(plugin_type=plugin_info['type']).count()
            plugin_info['amount_draft'] = CMSPlugin.objects.filter(plugin_type=plugin_info['type'],
                                                                   placeholder__page__publisher_is_draft=True).count()
            plugin_info['url'] = reverse('plugin_detail', kwargs={'plugin_type': plugin_info['type']})
            plugins_to_show.append(plugin_info)


        return plugins_to_show

    def get_context_data(self, **kwargs):
        context = super(PluginsList, self).get_context_data(**kwargs)
        form = DashboardFieldsForm()
        context.update({'forms': form})
        return context

    def get_queryset(self):
        range = self.request.GET.get("range") or None
        comparation = self.request.GET.get("comparation") or None
        keyword = self.request.GET.get("keyword") or None

        plugins = self.filter_plugins(keyword, plugin_pool.get_all_plugins(), range, comparation)
        qs = self.get_plugins_list(plugins)

        return qs

plugins_list = PluginsList.as_view()


# @login_required()
class PluginsDetail(DetailView):
    model = CMSPlugin
    template_name = 'djangocms_dashboard/plugin_detail.html'
    queryset = CMSPlugin.objects.all()

    def get_context_data(self, **kwargs):
        ctx = super(PluginsDetail, self).get_context_data(**kwargs)
        plugin_type = ctx['object'].plugin_type if ctx['object'] else ''
        qs = CMSPlugin.objects.filter(plugin_type=plugin_type).all()
        if qs:
            ctx['amount'] = qs.count()
            ctx['name'] = qs.first().get_plugin_name()
            ctx['type'] = qs.first().plugin_type
            ctx['instances'] = []
            for i in qs:
                # TODO: arrumar URL (delete_url e edit_url hard coded)
                ctx['instances'].append({
                    'title': i.page.get_title() if i.page else 'Placeholder Field',
                    'url': u'/' + i.page.get_path() if i.page else '',
                    'placeholder_label': i.placeholder.get_label(),
                    'placeholder_static': i.placeholder.is_static,
                    'not_published': i.page.publisher_is_draft if i.page else '',
                    'delete_url': u'/admin/cms/page/delete-plugin/' + unicode(i.pk),
                    'edit_url': u'/admin/cms/page/edit-plugin/' + unicode(i.pk),
                })
        return ctx

    def get_object(self, queryset=None):
        plugin_type = self.kwargs.get('plugin_type')
        obj = CMSPlugin.objects.filter(plugin_type=plugin_type).first()
        # obj = self.queryset.first()
        return obj


plugin_detail = PluginsDetail.as_view()


@login_required(login_url='')
def home(request):
    return render(request, 'djangocms_dashboard/home.html')


# @login_required()
class ApphooksList(ListView):
    template_name = 'djangocms_dashboard/apphooks_list.html'
    model = Page

    def get_context_data(self, **kwargs):
        ctx = super(ApphooksList, self).get_context_data(**kwargs)
        return ctx

    def get_queryset(self):
        # qs = super(ApphooksList, self).get_queryset()
        qs = []
        apphook_tuples = apphook_pool.get_apphooks()
        for apphook_tuple in apphook_tuples:
            apphook_info = {}
            apphook_info['name'] = unicode(apphook_tuple[1])
            apphook_info['class'] = unicode(apphook_tuple[0])
            apphook_info['amount'] = Page.objects.filter(application_urls=apphook_tuple[0],
                                                         publisher_is_draft=False).count()
            apphook_info['url'] = reverse('apphook_detail', kwargs={'apphook_class': apphook_info['class']})

            qs.append(apphook_info)

        return qs

apphooks_list = ApphooksList.as_view()

# @login_required()
class ApphooksDetail(DetailView):
    model = Page
    template_name = 'djangocms_dashboard/plugin_detail.html'
    queryset = Page.objects.all()

    def get_context_data(self, **kwargs):
        ctx = super(ApphooksDetail, self).get_context_data(**kwargs)
        apphook_class = self.kwargs.get('apphook_class')
        pages = Page.objects.filter(application_urls=apphook_class, publisher_is_draft=False).all()
        if pages:
            for page in pages:
                ctx['instances'].append({
                    'title': page.get_title(),
                    'url': u'/' + page.get_path(),
                    'not_published': page.publisher_is_draft
                })

        return ctx

    def get_object(self, queryset=None):
        apphook_class = self.kwargs.get('apphook_class')
        obj = Page.objects.filter(application_urls=apphook_class, publisher_is_draft=False).first
        return obj


apphook_detail = ApphooksDetail.as_view()




# def get_plugins_list(context, all_plugins, comparation, range):
#     context['plugins_info'] = []
#     for plugin_class in all_plugins:
#         plugin_info = {}
#         plugin_info['name'] = unicode(plugin_class.name)
#         plugin_info['type'] = unicode(plugin_class.__name__)
#         plugin_info['amount_published'] = CMSPlugin.objects.filter(plugin_type=plugin_info['type'],
#                                                                    placeholder__page__publisher_is_draft=False).count()
#         plugin_info['amount'] = CMSPlugin.objects.filter(plugin_type=plugin_info['type']).count()
#         plugin_info['amount_draft'] = CMSPlugin.objects.filter(plugin_type=plugin_info['type'],
#                                                                placeholder__page__publisher_is_draft=True).count()
#         plugin_info['url'] = reverse('plugin_detail', kwargs={'plugin_type': plugin_info['type']})
#
#         if not comparation or not range:
#             context['plugins_info'].append(plugin_info)
#         else:
#             if 'gte' in comparation:
#                 context['plugins_info'].append(plugin_info) if plugin_info['amount'] > int(range) else None
#             elif 'lte' in comparation:
#                 context['plugins_info'].append(plugin_info) if plugin_info['amount'] < int(range) else None
#             elif 'equ' in comparation:
#                 context['plugins_info'].append(plugin_info) if plugin_info['amount'] == int(range) else None
#
#     return context
#
# @login_required()
# def plugins_list(request):
#     context = {}
#     plugin_classes = plugin_pool.get_all_plugins()
#     form = DashboardFieldsForm()
#     range = request.POST.get("range") or None
#     comparation = request.POST.get("comparation") or None
#
#     get_plugins_list(context, plugin_classes, comparation, range)
#     context.update({'forms': form})
#
#     return render(request, 'djangocms_dashboard/plugins_list.html', context)



# @login_required()
# def plugin_detail(request, plugin_type):
#     context = {}
#     # context['name'] = plugin_name
#     # context['type'] = plugin_type
#     # context['amount'] = plugin_amount
#
#     instances = CMSPlugin.objects.filter(plugin_type=plugin_type)
#     if instances:
#         context['amount'] = instances.count()
#         context['name'] = instances.first().get_plugin_name()
#         context['type'] = instances.first().plugin_type
#         context['instances'] = []
#         for i in instances:
#     #TODO: arrumar URL (delete_url e edit_url hard coded)
#             context['instances'].append({
#                 'title': i.page.get_title() if i.page else 'Placeholder Field',
#                 'url': u'/' + i.page.get_path() if i.page else '',
#                 'placeholder_label': i.placeholder.get_label(),
#                 'placeholder_static': i.placeholder.is_static,
#                 'not_published': i.page.publisher_is_draft if i.page else '',
#                 'delete_url': u'/admin/cms/page/delete-plugin/' + unicode(i.pk),
#                 'edit_url': u'/admin/cms/page/edit-plugin/' + unicode(i.pk),
#             })
#     # pages = [_.]
#
#     return render(request, 'djangocms_dashboard/plugin_detail.html', context)



# @login_required()
# def get_apphook_class_name(apphook_obj):
#     return type(apphook_obj).__name__


# @login_required()
# def apphooks_list(request):
#     context = {}
#     apphook_tuples = apphook_pool.get_apphooks()
#     context['apphooks_info'] = []
#     for apphook_tuple in apphook_tuples:
#         apphook_info = {}
#         apphook_info['name'] = unicode(apphook_tuple[1])
#         apphook_info['class'] = unicode(apphook_tuple[0])
#         apphook_info['amount'] = Page.objects.filter(application_urls=apphook_tuple[0], publisher_is_draft=False).count()
#         apphook_info['url'] = reverse('apphook_detail', kwargs={'apphook_class': apphook_info['class']})
#
#         context['apphooks_info'].append(apphook_info)
#
#
#     return render(request, 'djangocms_dashboard/apphooks_list.html', context)





# @login_required()
# def apphook_detail(request, apphook_class):
#     context = {}
#     pages = Page.objects.filter(application_urls=apphook_class, publisher_is_draft=False)
#     context['class'] = apphook_class
#     context['amount'] = pages.count()
#     context['instances'] = []
#
#     if pages:
#         for page in pages:
#             context['instances'].append({
#                 'title': page.get_title(),
#                 'url': u'/' + page.get_path(),
#                 'not_published': page.publisher_is_draft
#             })
#
#     return render(request, 'djangocms_dashboard/apphook_detail.html', context)
