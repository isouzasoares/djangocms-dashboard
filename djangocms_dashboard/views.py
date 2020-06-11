# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from cms.apphook_pool import apphook_pool
from cms.models.pagemodel import Page
from cms.models.pluginmodel import CMSPlugin
from cms.plugin_pool import plugin_pool

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import DetailView, ListView

import unicodecsv as csv

from .forms import DashboardFieldsForm
from .utils import limpar_nome


try:
    from django.core.urlresolvers import reverse
except ImportError:
    from django.urls import reverse


class PluginsList(ListView):
    template_name = 'djangocms_dashboard/plugins_list.html'
    model = CMSPlugin
    csv_filename = 'csvfile.csv'
    paginate_by = 10

    def get_csv_filename(self):
        return self.csv_filename

    def render_to_response(self, context, **response_kwargs):
        response = super(PluginsList, self).render_to_response(
            context, **response_kwargs
        )
        if self.request.GET.get('export', '') == 'csv':
            response = self.get_csv_response()
        
        desc = self.request.GET.get('descp', '') or self.request.GET.get('descr', '')
        if desc == '':
            context.update({'order': False })
        else:
            if (self.request.GET.get('descp', '') != ''): 
                ordenacao = '&descp=' 
            else: 
                ordenacao = '&descr='
            
            desc = False if desc == 'False' else True
            ordenacao += str(desc)
            context.update({'order': not desc })
            context.update({'ordenacao': ordenacao })

        return response

    def lookingfor_plugins(self, keyword, plugins_list):
        if keyword:
            plugins_found = []
            for plugin in plugins_list:
                if keyword:
                    name = limpar_nome(plugin.name)
                    value = limpar_nome(plugin.value)
                    keyword = limpar_nome(keyword)
                    if keyword in name or keyword in value:
                        plugins_found.append(plugin)
            return plugins_found
        return plugins_list

    def filter_plugins(self, plugins_list, range, comparation, fields):
        if range and comparation:
            range = int(range)
            plugins_filtered = []

            for plugin in plugins_list:
                plugin.type = plugin.__name__
                filters = {
                    'plugin_type': plugin.type,
                    'placeholder__isnull': False,
                }
                if 'draft' in fields:
                    filters['placeholder__page__publisher_is_draft'] = True
                elif 'published' in fields:
                    filters['placeholder__page__publisher_is_draft'] = False
                plugin.amount = CMSPlugin.objects.filter(**filters).count()

                if 'gte' in comparation and plugin.amount > range:
                    plugins_filtered.append(plugin)
                elif 'lte' in comparation and plugin.amount < range:
                    plugins_filtered.append(plugin)
                elif 'equ' in comparation and plugin.amount == range:
                    plugins_filtered.append(plugin)

            return plugins_filtered
        return plugins_list

    def get_plugins_list(self, plugins):
        plugins_to_show = []
        for plugin in plugins:
            plugin_info = {}
            plugin_info['name'] = plugin.name
            plugin_info['type'] = plugin.__name__

            qs = CMSPlugin.objects.filter(plugin_type=plugin_info['type'])
            qs_pub = qs.filter(placeholder__page__publisher_is_draft=False)
            qs_draft = qs.filter(placeholder__page__publisher_is_draft=True)

            plugin_info.update({
                'amount': qs.count(),
                'amount_published': qs_pub.count(),
                'amount_draft': qs_draft.count(),
            })

            plugin_info['url'] = reverse(
                'plugin_detail',
                kwargs={'plugin_type': plugin_info['type']}
            )
            plugins_to_show.append(plugin_info)

        if (self.request.GET.get('descp', '') or self.request.GET.get('descr', '')):
            plugins_to_show = self.ordena_lista(plugins_to_show)

        return plugins_to_show

    def get_context_data(self, **kwargs):
        context = super(PluginsList, self).get_context_data(**kwargs)
        form = DashboardFieldsForm(self.request.GET)
        context.update({'forms': form})
        return context

    def get_queryset(self):
        range = self.request.GET.get("range")
        comparation = self.request.GET.get("comparation")
        keyword = self.request.GET.get("keyword")
        fields = self.request.GET.get("fields_search")
        plugins_found = self.lookingfor_plugins(
            keyword, plugin_pool.get_all_plugins()
        )
        plugins_filtered = self.filter_plugins(
            plugins_found, range, comparation, fields
        )

        return self.get_plugins_list(plugins_filtered)

    def get_csv_response(self):
        response = HttpResponse(content_type='text/csv')
        csv_filename = 'attachment; filename="%s"' % self.get_csv_filename()
        response['Content-Disposition'] = csv_filename

        writer = csv.writer(response)
        writer.writerow(['Lista de Plugins Dashboard'])
        writer.writerow([
            'Nome', 'Tipo (Classe)', 'Quantidade Publicada',
            'Quantidade Rascunho', 'Url de acesso',
        ])
        for lst in self.object_list:
            url = lst['url']
            qtde = lst['amount_published']
            del lst['amount']
            del lst['url']
            lst['amount_published'] = lst['type']
            lst['type'] = qtde
            lst[5] = url

            writer.writerow(list(lst.values()))

        return response

    def ordena_lista(self, lista_plugins):        
        desc = self.request.GET.get('descp', '') or self.request.GET.get('descr', '')
        
        if desc == '':
            descendente = False
        else:
            descendente = False if desc == 'False' else True

            if self.request.GET.get('descp', '') != '':
                order_by =  'amount_published'
            else:
                order_by =  'amount_draft'

        newlist = sorted(lista_plugins, key=lambda k: k[order_by], reverse=descendente) 

        return newlist


plugins_list = PluginsList.as_view()


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
                pk = str(i.pk)
                base_url_page = u'/admin/cms/page/%s/' + pk
                # TODO: arrumar URL (delete_url e edit_url hard coded)
                instance = {
                    'title': 'PlaceholderField',
                    'url': '',
                    'placeholder_label': i.placeholder.get_label(),
                    'placeholder_static': i.placeholder.is_static,
                    'not_published': '',
                    'delete_url': base_url_page % 'delete-plugin',
                    'edit_url': base_url_page % 'edit-plugin',
                }
                if i.page:
                    instance.update({
                        'title': i.page.get_title(),
                        'url': u'/' + i.page.get_path(),
                        'not_published': i.page.publisher_is_draft,
                    })
                ctx['instances'].append(instance)
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
        context = super(ApphooksList, self).get_context_data(**kwargs)
        desc = self.request.GET.get('desc', '')

        apphooks_list = context['object_list']

        if self.request.GET.get('desc', '') != '':
            desc = False if desc == 'False' else True
            apphooks_list = sorted(apphooks_list, key=lambda k: k[u'amount'], reverse=desc)
            context.update({'object_list': apphooks_list})
            context.update({'order': not desc })
        else:
            context.update({'order': True })

        return context

    def get_queryset(self):
        # qs = super(ApphooksList, self).get_queryset()
        qs = []
        apphook_tuples = apphook_pool.get_apphooks()
        for apphook_tuple in apphook_tuples:
            apphook_info = {}
            apphook_info['name'] = apphook_tuple[1]
            apphook_info['class'] = apphook_tuple[0]
            apphook_info['amount'] = Page.objects.filter(
                application_urls=apphook_tuple[0],
                publisher_is_draft=False
            ).count()
            apphook_info['url'] = reverse(
                'apphook_detail',
                kwargs={'apphook_class': apphook_info['class']}
            )

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
        pages = Page.objects.filter(
            application_urls=apphook_class,
            publisher_is_draft=False
        )
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
        obj = Page.objects.filter(
            application_urls=apphook_class,
            publisher_is_draft=False
        ).first()
        return obj


apphook_detail = ApphooksDetail.as_view()
