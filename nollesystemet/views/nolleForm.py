import json
from typing import Any

from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, FormView, UpdateView

import nollesystemet.mixins as mixins
import nollesystemet.models as models
from nollesystemet.forms import NolleFormBaseForm, NolleFormAdministrationForm, ValidationError
from .misc import DownloadView, ObjectsAdministrationListView


class NolleFormManageView(mixins.FohserietMixin, ObjectsAdministrationListView):
    model = models.NolleFormAnswer
    form_class = NolleFormAdministrationForm

    template_name = "fohseriet/nolleenkaten/index.html"

    login_required = True
    permission_required = 'nollesystemet.edit_nolleForm'

    success_url = reverse_lazy('fohseriet:nolleenkaten:index')

    def get_form_kwargs(self):
        context = super().get_form_kwargs()
        context['can_delete'] = self.request.user.is_superuser
        return context

    def form_valid(self, form):
        models.NolleFormAnswer.objects.all().delete()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['preview_form'] = NolleFormBaseForm(editable=True, form_tag=False)
        context['num_of_answers'] = models.NolleFormAnswer.objects.all().count()
        return context

    def handle_uploaded_file(self, file_data):
        if file_data:
            models.NolleFormAnswer.objects.all().delete()
            try:
                models.DynamicNolleFormQuestion.set_questions_from_dict(file_data)
            except SyntaxError as e:
                self.file_upload_success = False
                self.file_upload_information = "Error thrown: %s" % e.msg
            else:
                self.file_upload_success = True
                self.file_upload_information = "Uppladdning lyckades!"
        else:
            self.file_upload_success = False
            self.file_upload_information = "File data is empty"

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

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form, form_failed=True))


class NolleFormDownloadView(mixins.FohserietMixin, DownloadView):
    login_required = True
    permission_required = 'nollesystemet.edit_nolleForm'
    file_name = "Svar_nolleenkaten"

    @staticmethod
    def get_user_program(answer: models.NolleFormAnswer):
        return str(answer.user.program_name)

    @staticmethod
    def get_static_model_value(answer: models.NolleFormAnswer, field_name):
        if hasattr(answer, field_name): # Non-dynamic question
            return getattr(answer, field_name)
        else:
            return ""

    @staticmethod
    def get_dynamic_value(answer: models.NolleFormAnswer, dynamic_question):
        try:
            ans = models.DynamicNolleFormQuestionAnswer.objects.filter(
                question=dynamic_question,
                nolleformanswer__user=answer.user
            )
        except models.DynamicNolleFormQuestionAnswer.DoesNotExist:
            return ""
        else:
            if dynamic_question.question_type == models.DynamicNolleFormQuestion.QuestionType.TEXT:
                if ans.count() == 1:
                    return ans[0].value
                else:
                    return ""
            elif dynamic_question.question_type == models.DynamicNolleFormQuestion.QuestionType.RADIO:
                if ans.count() == 1:
                    if ans[0].group:
                        return ans[0].group
                    else:
                        return ans[0].value
                else:
                    return ""
            else:
                try:
                    return ", ".join([a.group if a.group else a.value for a in ans.all()])
                except:
                    return ""

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.empty_form = NolleFormBaseForm()
        self.non_dynamic_fields = [val for val in NolleFormBaseForm().fields if not val[:2] == "q_"]
        self.csv_data_structure: Any = [
            {'title': 'username', 'accessor': 'user.auth_user.username'},
            {'title': 'program', 'function': self.get_user_program}
        ]
        self.csv_data_structure += [
            {
                'title': self.empty_form.fields[field_name].label,
                'function': self.get_static_model_value,
                'args': (field_name,)
            } for field_name in self.non_dynamic_fields
        ]
        self.csv_data_structure += [
            {
                'title': question.title,
                'function': self.get_dynamic_value,
                'args': (question,)
            } for question in models.DynamicNolleFormQuestion.objects.all()
        ]

    def get_queryset(self):
        return models.NolleFormAnswer.objects.all()
