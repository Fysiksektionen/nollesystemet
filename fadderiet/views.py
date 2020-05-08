from django.shortcuts import HttpResponse
from django.urls import reverse
from django.views.generic.base import ContextMixin, TemplateView

import fadderiet.utils as utils


def hello_world(request, *args, **kwargs):
    return HttpResponse("Hello world!\n You are at: " + request.get_full_path_info())

def custom_redirect_view(request, redirect_name, keep_GET_params=True, default_GET_params=None, url_args=None):
    GET_params = default_GET_params
    if not default_GET_params:
        GET_params = {}
    GET_params.update(request.GET)

    if not url_args:
        url_args = []
    if not keep_GET_params or not GET_params:
        GET_params = {}

    return utils.custom_redirect(redirect_name, *url_args, **GET_params)

class MenuBaseMixin(ContextMixin):

    menu_items = []
    menu_item_info = None

    def get_context_data(self, **kwargs):
        if len(self.menu_items) > 0 and not self.menu_item_info:
            raise ReferenceError("menu_item_info not set, with menu_items specified.")

        menu = {'left': [], 'right': []}
        for item in self.menu_items:
            menu[self.menu_item_info[item]['align']].append({
                **self.menu_item_info[item],
                'url': reverse(self.menu_item_info[item]['url_name'])
            })

        context = {}
        if menu:
            context['menu'] = menu
        return super().get_context_data(**kwargs, **context)


class MenuBaseView(MenuBaseMixin, TemplateView):
    pass
