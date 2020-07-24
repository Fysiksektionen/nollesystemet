import json
from typing import Any

from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, FormView, UpdateView

import nollesystemet.mixins as mixins
import nollesystemet.models as models
from nollesystemet.forms import NolleFormBaseForm, NolleFormFileUploadForm
from .misc import DownloadView


class NolleFormManageView(mixins.FohserietMixin, FormView):
    login_required = True
    permission_required = 'nollesystemet.edit_nolleForm'

    template_name = "fohseriet/nolleenkaten/index.html"

    form_class = NolleFormFileUploadForm
    success_url = reverse_lazy('fohseriet:nolleenkaten:index')

    def form_valid(self, form):
        models.NolleFormAnswer.objects.all().delete()
        form.update_nolleForm()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['preview_form'] = NolleFormBaseForm(editable=True, form_tag=False)
        context['num_of_answers'] = models.NolleFormAnswer.objects.all().count()
        return context

class NolleFormView(mixins.FadderietMixin, UpdateView):
    site_name = 'Fadderiet: nØlleenkäten'
    site_texts = ['body']

    template_name = "fadderiet/nolleenkaten/visa.html"
    form_class = NolleFormBaseForm
    login_required = True

    def test_func(self):
        return models.NolleFormAnswer.can_fill_out(self.request.user.profile)

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
    permission_required = 'nollesystemet:edit_nolleForm'
    file_name = "Svar_nolleenkaten"

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

    def get_queryset(self):
        return models.NolleFormAnswer.objects.all()


class NolleFormDeleteView(mixins.FohserietMixin, FormView):
    login_required = True
    permission_required = 'nollesystemet:edit_nolleForm'

    def get(self, request, *args, **kwargs):
        models.NolleFormAnswer.objects.all().delete()
        return HttpResponseRedirect(reverse('fohseriet:nolleenkaten:index'))
