import collections
import csv
from abc import abstractmethod
from typing import Any, Callable

from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from django.http import QueryDict, HttpResponseRedirect, HttpResponse
from django.views import View
from django.views.generic import TemplateView, UpdateView

import authentication.models as auth_models
import nollesystemet.mixins as mixins
from nollesystemet.models import NolleGroup


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
        context['nolle_groups'] = NolleGroup.objects.all()
        try:
            context['users_nolle_group'] = self.request.user.profile.nolle_group if self.request.user else ''
        except:
            pass
        return context

class DownloadView(View):
    # {'title': '', 'accessor': ''} or
    # {'title': '', 'function': },
    csv_data_structure: Any = []

    file_name = None

    def get_file_name(self):
        return ""

    def get_queryset(self):
        return []

    def get(self, request, *args, **kwargs):
        if self.file_name is None:
            self.file_name = self.get_file_name()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="' + self.file_name + '.csv"'
        writer = csv.writer(response)

        # Write column titles
        writer.writerow([column['title'] for column in self.csv_data_structure])

        # Write registration data
        queryset = self.get_queryset()
        row_data = []
        for item in queryset:
            column_data = []

            for column in self.csv_data_structure:
                value = None
                if 'accessor' in column:
                    accessor_path = column['accessor']
                    current_node = item
                    while '.' in accessor_path:
                        index = accessor_path.find('.')
                        next_accessor = accessor_path[:index]
                        accessor_path = accessor_path[index+1:]

                        current_node = current_node.__getattribute__(next_accessor)
                    value = current_node.__getattribute__(accessor_path)

                elif 'function' in column:
                    fn: Callable = column['function']
                    fn_args = column.get('args', [])
                    value = fn(item, *fn_args)

                else:
                    raise SyntaxError("No valid way of obtaining data was presented. Either specify an 'accessor' path or a 'function' to run to obtain data." )

                if value is None or isinstance(value, str):
                    pass
                elif isinstance(value, collections.abc.Iterable):
                    value = ', '.join([str(v) for v in value])
                elif isinstance(value, object):
                    value = str(value)
                column_data.append(value)

            row_data.append(column_data)

        writer.writerows(row_data)
        return response
