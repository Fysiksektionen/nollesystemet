from abc import abstractmethod

from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import HttpResponse
from django.urls import reverse
from django.views.generic import UpdateView
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
        for items in self.menu_items:
            if not isinstance(items, list):
                items = [items]

            for item in items:
                info = self.menu_item_info[item]

                render = info['user'] == 'any' \
                         or (info['user'] == 'logged-in' and self.request.user.is_authenticated) \
                         or (info['user'] == 'logged-out' and not self.request.user.is_authenticated)

                if render:
                    menu[info['align']].append({
                        **info,
                        'url': reverse(info['url_name'])
                    })
                    break

        context = {}
        if menu:
            context['menu'] = menu
        return super().get_context_data(**kwargs, **context)


class MenuBaseView(MenuBaseMixin, TemplateView):
    menu_item_info = utils.menu_item_info
    menu_items = ['index', 'schema', 'bra-info', 'anmal-dig', 'kontakt', ['mina-sidor:profil', 'logga-in'], 'logga-ut']

class MultipleObjectsUpdateView(UpdateView):
    model_list = None
    fields_list = None
    form_class_list = None
    fill_with_object_data = True
    initial_list = None
    make_forms_crispy = True

    def get_form_class(self):
        """Return a list of form classes to use in this view."""
        if self.fields_list is not None and self.form_class_list:
            raise ImproperlyConfigured(
                "Specifying both 'fields_list' and 'form_class_list' is not permitted."
            )
        if self.form_class_list:
            return self.form_class_list
        else:
            return_list = []

            if self.fields_list is None:
                raise ImproperlyConfigured(
                    "Using MultipleObjectsUpdateView (base class of %s) without "
                    "the 'fields_list' attribute is prohibited." % self.__class__.__name__
                )
            if len(self.model_list) != len(self.fields_list):
                raise ImproperlyConfigured(
                    "'model_list' and 'fields_list' are not of the same length."
                )

            for model, fields in zip(self.model_list, self.fields_list):
                self.model = model
                self.fields = fields
                return_list.append(super().get_form_class())

            return return_list

    def get_form(self, form_class_list=None):
        """Return list of forms with correct kwargs."""
        if form_class_list is None:
            form_class_list = self.get_form_class()

        form_list = []
        kwargs = self.get_form_kwargs()
        list_kwargs = ['instance', 'initial', 'prefix']

        for i, form_class in enumerate(form_class_list):
            form_kwargs = kwargs.copy()
            for arg in list_kwargs:
                if arg in form_kwargs:
                    if isinstance(kwargs[arg], list) and kwargs[arg]:
                        form_kwargs.update({arg: kwargs[arg][i]})
                    else:
                        form_kwargs.pop(arg)
            form_list.append(form_class(**form_kwargs))

        if self.make_forms_crispy:
            for form in form_list:
                from crispy_forms.helper import FormHelper
                setattr(form, 'helper', FormHelper())
                form.helper.form_tag = False

        return form_list

    def get_object(self, queryset=None):
        """Inherited internally used method."""
        return list(self.get_objects())

    @abstractmethod
    def get_objects(self):
        """Override in child class."""
        pass

    def get_prefix(self):
        """Add prefix to differ forms."""
        num_of_models = len(self.form_class_list) if self.form_class_list else len(self.fields_list)
        return ['form' + str(i) for i in range(num_of_models)]

    def get_initial(self):
        if self.initial_list:
            return self.initial_list
        else:
            return None

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        self.object = self.get_object()

        forms = self.get_form()
        for form in forms:
            if not form.is_valid():
                return self.form_invalid(form)

        return self.form_valid(forms)

    def form_valid(self, forms):
        """If the form is valid, save the associated model."""
        self.object = [form.save() for form in forms]
        from django.views.generic.edit import FormMixin
        return FormMixin.form_valid(self, forms)

    def get_success_url(self):
        from django.views.generic.edit import FormMixin
        return FormMixin.get_success_url(self)
