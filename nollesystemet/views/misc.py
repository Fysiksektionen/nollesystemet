from abc import abstractmethod

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from django.http import QueryDict, HttpResponseRedirect, HttpResponse
from django.views.generic import TemplateView, UpdateView

import authentication.models as auth_models

import nollesystemet.mixins as mixins
from nollesystemet import models



class FadderietMenuView(mixins.FadderietMixin, TemplateView):
    pass


class FohserietMenuView(mixins.FohserietMixin, TemplateView):
    pass


def custom_redirect(url_name, *args, query_dict=None, **kwargs):
    url = reverse(url_name, args=args)
    if not query_dict:
        query_dict = QueryDict()
    query_dict.update(kwargs)
    params = query_dict.urlencode(safe='/')
    return HttpResponseRedirect(url + "?%s" % params)


def hello_world(request, *args, **kwargs):
    return HttpResponse("Hello world!\n You are at: " + request.get_full_path_info())


def custom_redirect_view(request, redirect_name, keep_GET_params=True, default_GET_params=None, url_args=None):
    query_dict = request.GET.copy()
    if default_GET_params:
        query_dict.update(default_GET_params)

    if not url_args:
        url_args = []
    if not keep_GET_params:
        query_dict = None

    return custom_redirect(redirect_name, *url_args, query_dict=query_dict)


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
                if not hasattr(form, 'helper'):
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
                return self.form_invalid(forms)

        return self.form_valid(forms)

    def form_valid(self, forms):
        """If the form is valid, save the associated model."""
        self.object = [form.save() for form in forms]
        from django.views.generic.edit import FormMixin
        return FormMixin.form_valid(self, forms)

    def get_success_url(self):
        from django.views.generic.edit import FormMixin
        return FormMixin.get_success_url(self)


class ScheduleView(mixins.FadderietMixin, TemplateView):
    template_name = "fadderiet/schema.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nolle_groups'] = auth_models.NolleGroup.objects.all()
        try:
            context['users_nolle_group_name'] = self.request.user.nolle_group.name if self.request.user else ''
        except:
            pass
        return context
