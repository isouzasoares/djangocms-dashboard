# -*- coding: utf-8 -*-
from django.core.paginator import Paginator
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from cms.apphook_pool import apphook_pool
from cms.models.pagemodel import Page
from cms.models.pluginmodel import CMSPlugin
from cms.plugin_pool import plugin_pool, PluginPool
from django.template.defaultfilters import slugify

from .forms import DashboardFieldsForm
from django.views.generic import DetailView, ListView
from unicodedata import normalize
import csv
from django.http import HttpResponse


try:
    from django.core.urlresolvers import reverse
except ImportError:
    from django.urls import reverse


def remover_espacos(n):
    return ' '.join(n.split())


def remover_acentos(txt):
    return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')


def limpar_nome(nome):
    sem_espacos = remover_espacos(unicode(nome))
    return remover_acentos(sem_espacos).lower()


class CSVResponseMixin(object):
    csv_filename = 'csvfile.csv'

    def get_csv_filename(self):
        return self.csv_filename

    def render_to_csv(self, data):
        response = HttpResponse(content_type='text/csv')
        cd = 'attachment; filename="{0}"'.format(self.get_csv_filename())
        response['Content-Disposition'] = cd

        writer = csv.writer(response)
        writer.writerow(['Lista de Plugins Dashboard'])
        writer.writerow(['Nome', 'Tipo (Classe)', 'Quantidade Publicada', 'Quantidade Rascunho', 'Url de acesso'])
        for lst in data:
            url = lst['url']
            qtde = lst['amount_published']
            del lst['amount']
            del lst['url']
            lst['amount_published'] = lst['type']
            lst['type'] = qtde
            lst[5] = url

            writer.writerow(list(lst.values()))
        return response

class PluginsList(CSVResponseMixin, ListView):
    template_name = 'djangocms_dashboard/plugins_list.html'
    model = CMSPlugin



    def lookingfor_plugins(self, keyword, plugins_list):
        if keyword:
            plugins_found = []
            for plugin in plugins_list:
                if keyword:
                    keyword = unicode(keyword)
                    plugins_found.append(plugin) if limpar_nome(keyword) in limpar_nome(plugin.name) or limpar_nome(keyword) in limpar_nome(unicode(plugin.value)) else None
            return plugins_found
        return plugins_list

    def filter_plugins(self, plugins_list, range, comparation, fields):
        if range and comparation:
            plugins_filtered = []

            for plugin in plugins_list:
                plugin.type = unicode(plugin.__name__)
                plugin.amount = CMSPlugin.objects.filter(plugin_type=plugin.type, placeholder__page__publisher_is_draft=True).count() if 'draft' in fields else None
                plugin.amount = CMSPlugin.objects.filter(plugin_type=plugin.type, placeholder__page__publisher_is_draft=False).count() if 'published' in fields else CMSPlugin.objects.filter(plugin_type=plugin.type).count()

                if 'gte' in comparation:
                    plugins_filtered.append(plugin) if plugin.amount > int(range) else None
                elif 'lte' in comparation:
                    plugins_filtered.append(plugin) if plugin.amount < int(range) else None
                elif 'equ' in comparation:
                    plugins_filtered.append(plugin) if plugin.amount == int(range) else None

            return plugins_filtered
        return plugins_list

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

        parametros = ''
        for key in self.request.GET:
            if key is not 'page' and key != 'page':
                value = self.request.GET.get(key) or None
                if value is not None:
                    parametros += '&{key}={value}'.format(key=key, value=value)

        context.update({'forms': form, 'parametros': parametros})

        return context

    def get_queryset(self):
        range = self.request.GET.get("range") or None
        comparation = self.request.GET.get("comparation") or None
        keyword = self.request.GET.get("keyword") or None
        fields = self.request.GET.get("fields_search") or None
        plugins_found = self.lookingfor_plugins(keyword, plugin_pool.get_all_plugins())
        plugins_filtered = self.filter_plugins(plugins_found, range, comparation, fields)

        qs = self.get_plugins_list(plugins_filtered)
        paginator = Paginator(qs, 10)
        page = self.request.GET.get('page')
        if page is None:
            page = 1
        return paginator.page(page)


    def export_csv(self, request, *args, **kwargs):
        range = self.request.GET.get("range") or None
        comparation = self.request.GET.get("comparation") or None
        keyword = self.request.GET.get("keyword") or None
        fields = self.request.GET.get("fields_search") or None
        plugins_found = self.lookingfor_plugins(keyword, plugin_pool.get_all_plugins())
        plugins_filtered = self.filter_plugins(plugins_found, range, comparation, fields)

        qs = self.get_plugins_list(plugins_filtered)

        return self.render_to_csv(qs)


plugins_list = PluginsList.as_view()
export = PluginsList.export_csv()


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
        return obj


plugin_detail = PluginsDetail.as_view()


@login_required(login_url='')
def home(request):
    return render(request, 'djangocms_dashboard/home.html')


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
