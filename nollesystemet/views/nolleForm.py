import json
from typing import Any

from django.contrib.staticfiles import finders
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, FormView, UpdateView

import nollesystemet.mixins as mixins
import nollesystemet.models as models
from nollesystemet.forms import NolleFormBaseForm
from .misc import DownloadView


class NolleFormInspectView(mixins.FohserietMixin, FormView):
    login_required = True
    permission_required = 'nollesystemet:edit_user_info'

    template_name = "fohseriet/nolleenkaten/index.html"

    form_class = NolleFormBaseForm

    def post(self, request, *args, **kwargs):
        if 'update' in request.POST:
            models.DynamicQuestion.objects.all().delete()

            with open(finders.find('fohseriet/resources/nolleFormInfo.json')) as json_file:
                data = json.load(json_file)
                for question_info in data['dynamic_questions']:
                    models.DynamicQuestion(question_info=question_info)
        return self.get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'editable': False,
            'form_tag': False
        })
        return kwargs


class NolleFormView(mixins.FadderietMixin, UpdateView):
    login_required = True
    template_name = "fadderiet/nolleenkaten/visa.html"
    form_class = NolleFormBaseForm

    def get_object(self, queryset=None):
        try:
            return models.NolleFormAnswer.objects.get(user=self.request.user.profile)
        except models.NolleFormAnswer.DoesNotExist:
            return None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.object:
            kwargs['editable'] = False
        else:
            kwargs['submit_name'] = "Skicka"
        kwargs['user'] = self.request.user.profile
        return kwargs

    def get_success_url(self):
        return reverse('fadderiet:index')


class NolleFormDownloadView(mixins.FohserietMixin, DownloadView):
    login_required = True
    permission_required = 'nollesystemet:edit_user_info'

    @staticmethod
    def get_field_value(answer, field_name):
        form = NolleFormBaseForm(instance=answer)
        if hasattr(form.fields[field_name], 'choices'):
            choices = form.fields[field_name].choices
            initial = form.initial[field_name] if isinstance(form.initial[field_name], list) else [
                form.initial[field_name]]

            def get_choices(initial_value):
                return [choice[1] for choice in choices if choice[0] == str(initial_value)]
            return [get_choices(initial_value)[0] for initial_value in initial if get_choices(initial_value) != []]
        else:
            return form.initial[field_name]

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        form = NolleFormBaseForm()
        self.csv_data_structure: Any = [
            {
                'title': form.fields[field_name].label,
                'function': self.get_field_value,
                'args': (field_name,)
            }
            for field_name in form.fields
        ]

    file_name = "Svar_nolleenkaten"

    def get_queryset(self):
        return models.NolleFormAnswer.objects.all()
