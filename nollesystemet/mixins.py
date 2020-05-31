import json

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.template import Template, Context
from django.urls import reverse
from django.views.generic.base import ContextMixin
from django.contrib.staticfiles import finders


class HappeningOptionsMixin:
    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = super().get_form(form_class)
        return form

    def form_valid(self, form):
        context = self.get_context_data(form=form)
        drink_option_formset = context['drink_option_formset']
        base_price_formset = context['base_price_formset']
        extra_option_formset = context['extra_option_formset']
        if drink_option_formset.is_valid() and base_price_formset.is_valid() and extra_option_formset.is_valid():
            response = super().form_valid(form)

            drink_option_formset.instance = self.object
            drink_option_formset.save()

            base_price_formset.instance = self.object
            base_price_formset.save()

            extra_option_formset.instance = self.object
            extra_option_formset.save()
            return response
        else:
            return super().form_invalid(form)


class MenuMixin(ContextMixin):
    menu_items_static_file = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        menu_items = None
        order = None
        try:
            with open(finders.find(self.menu_items_static_file)) as json_file:
                data = json.load(json_file)
                order = data['order']
                menu_items = data['menu_items']
        except:
            raise FileNotFoundError("menu_items_static_file not set or not able to be read.")

        if not order or not menu_items:
            raise SyntaxError("order or menu_items not found in file %s" % finders.find(self.menu_items_static_file))

        menu = {'left': [], 'right': []}
        for items in order:
            if not isinstance(items, list):
                items = [items]

            for item in items:
                info = menu_items[item]

                render = self.check_if_to_render(info)

                if render:
                    menu[info['align']].append({
                        **info,
                        'url': reverse(info['url_name'])
                    })

                    if menu[info['align']][-1]['url'] == self.request.path:
                        menu[info['align']][-1]['classes'] = (info['classes'] + ' ' if 'classes' in info else '') + 'selected-menu-item'
                    break

        if menu:
            context['menu'] = menu
        return context

    def check_if_to_render(self, info):
        if info['user'] == 'any':
            return True

        if info['user'] == 'logged-in' and self.request.user.is_authenticated:
            return True

        if info['user'] == 'logged-out' and not self.request.user.is_authenticated:
            return True

        if info['user'] == 'with-permission':
            render = True
            for logic, prems in info['permissions'].items():
                if logic == 'all':
                    for prem in prems:
                        if not self.request.user.has_perm(prem):
                            render = False
                elif logic == 'any':
                    for prem in prems:
                        if self.request.user.has_perm(prem):
                            break
                    else:
                        render = False
                else:
                    raise Exception("Permissions can only contain keys 'any' or 'all', not %s" % logic)

            return render

        return False

    def render_to_response(self, context, **response_kwargs):
        if 'menu' in context:
            for side in ['left', 'right']:
                if side in context['menu']:
                    for i, menu_item in enumerate(context['menu'][side]):
                        if 'template_content' in menu_item:
                            context['menu'][side][i]['template_content'] = Template(menu_item['template_content']).render(Context({**context, 'user': self.request.user, 'request': self.request}))

        return super().render_to_response(context, **response_kwargs)


class RedirectToGETArgMixin:
    def get_success_url(self):
        if REDIRECT_FIELD_NAME in self.request.GET:
            self.success_url = self.request.GET[REDIRECT_FIELD_NAME]
        return super().get_success_url()


class FohserietMenuMixin(MenuMixin):
    menu_items_static_file = 'fohseriet/resources/menu_info.json'


class FadderietMenuMixin(MenuMixin):
    menu_items_static_file = 'fadderiet/resources/menu_info.json'
