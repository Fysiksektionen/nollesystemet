import json
import io
from crispy_forms.helper import FormHelper
from django import forms
from crispy_forms.layout import Layout, Fieldset, Field, Row, Column, HTML, Submit, Div

from .misc import ModifiableModelForm
from nollesystemet.models import NolleFormAnswer, DynamicNolleFormQuestion, DynamicNolleFormQuestionAnswer

class NolleFormFileUploadForm(forms.Form):
    nolle_form_file = forms.FileField(label='Fil med frågor (*.json)',
                                      required=True,
                                      allow_empty_file=False,
                                      help_text="Här laddar du upp en fil som uppdaterar innehållet i nØlleformuläret.")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'nolle_form_file',
            Submit('submit', 'Uppdatera formulär', css_class="col-5"),
        )
        self.helper.form_method = 'post'

    def update_nolleForm(self):
        if self.cleaned_data and 'json_data' in self.cleaned_data:
            NolleFormAnswer.objects.all().delete()
            DynamicNolleFormQuestion.set_questions_from_dict(self.cleaned_data['json_data'])
        else:
            raise AttributeError("Form is not bound and cleaned. 'json_data' not found.")

    def clean_nolle_form_file(self):
        try:
            data = json.load(self.cleaned_data['nolle_form_file'])
            self.cleaned_data['json_data'] = data
        except:
            raise forms.ValidationError("File is not a valid json file.")

        validation_errors = DynamicNolleFormQuestion.validate_questions_from_dict(data)
        if validation_errors:
            raise forms.ValidationError("\n".join(validation_errors))


class DynamicQuestionCharField(forms.CharField):
    def __init__(self, question, **kwargs):
        self.question = question
        super().__init__(**kwargs)

    def clean(self, value):
        cleaned_value = super().clean(value)
        try:
            return DynamicNolleFormQuestionAnswer.objects.get(question=self.question, value=cleaned_value)
        except DynamicNolleFormQuestionAnswer.DoesNotExist:
            return DynamicNolleFormQuestionAnswer(question=self.question, value=cleaned_value)


class NolleFormBaseForm(ModifiableModelForm):
    class Meta:
        model = NolleFormAnswer
        fields = '__all__'

        field_args = {
            'first_name': {
                'label': 'Jag heter',
                'required': True,
            },
            'last_name': {
                'label': ' ',
                'required': True,
            },
            'nick_name': {
                'label': 'men jag kallas',
            },
            'age': {
                'label': 'Min ålder är'
            },
            'age_feeling': {
                'label': 'men jag känner mig som'
            },
            'home_address': {
                'label': 'Under mottagningen bor jag på',
            },
            'phone_number': {
                'label': 'och ni når mig på',
            },
            'contact_name': {
                'label': 'Namn',
            },
            'contact_relation': {
                'label': 'Relation',
            },
            'contact_phone_number': {
                'label': 'Mobilnummer',
            },
            'food_preference': {
                'label': 'Matpreferens',
                'widget_class': forms.widgets.Textarea,
                'widget_attrs': {'rows': 3},
            },
            'other': {
                'label': 'Övrigt',
                'widget_class': forms.widgets.Textarea,
                'widget_attrs': {'rows': 3}
            },
            'about_the_form': {
                'label': 'Om formuläret'
            }
        }

    def __init__(self, user=None, **kwargs):
        super().__init__(**kwargs)
        if user:
            self.instance.user = user

    def add_fields(self, **kwargs):
        for question in DynamicNolleFormQuestion.objects.all():
            if question.question_type == DynamicNolleFormQuestion.QuestionType.TEXT:
                self.fields['q_' + str(question.pk)] = DynamicQuestionCharField(
                    question,
                    max_length=DynamicNolleFormQuestionAnswer._meta.get_field('value').max_length,
                    widget=forms.Textarea(attrs={"rows": 2})
                )
                if not self.is_new:
                    self.initial['q_' + str(question.pk)] = self.instance.dynamic_answers.get(question=question).value
            elif question.question_type == DynamicNolleFormQuestion.QuestionType.RADIO:
                self.fields['q_' + str(question.pk)] = forms.ChoiceField(
                    choices=[(str(q.pk), str(q.value)) for q in question.dynamicnolleformquestionanswer_set.all()],
                    widget=forms.RadioSelect
                )
                if not self.is_new:
                    self.initial['q_' + str(question.pk)] = self.instance.dynamic_answers.get(question=question).pk
            elif question.question_type == DynamicNolleFormQuestion.QuestionType.CHECK:
                self.fields['q_' + str(question.pk)] = forms.MultipleChoiceField(
                    choices=[(str(q.pk), str(q.value)) for q in question.dynamicnolleformquestionanswer_set.all()],
                    widget=forms.CheckboxSelectMultiple
                )
                if not self.is_new:
                    pks = list(self.instance.dynamic_answers.filter(question=question).values_list('pk'))
                    self.initial['q_' + str(question.pk)] = [str(tup[0]) for tup in pks]
            self.fields['q_' + str(question.pk)].label = '<strong>' + question.number_label + '</strong>. ' + question.title

        if not self.is_editable:
            for field_name in self.fields:
                self.fields[field_name].disabled = True
                self.fields[field_name].widget.disabled = True

    def save(self, commit=True):
        super().save(commit=commit)
        for field_name in self.fields:
            if field_name[:2] == 'q_':
                question = DynamicNolleFormQuestion.objects.get(pk=field_name[2:])

                if question.question_type == DynamicNolleFormQuestion.QuestionType.TEXT:
                    self.cleaned_data[field_name].save()
                    self.instance.dynamic_answers.add(self.cleaned_data[field_name])
                elif question.question_type == DynamicNolleFormQuestion.QuestionType.RADIO:
                    self.instance.dynamic_answers.add(DynamicNolleFormQuestionAnswer.objects.get(pk=self.cleaned_data[field_name]))
                elif question.question_type == DynamicNolleFormQuestion.QuestionType.CHECK:
                    for pk in self.cleaned_data[field_name]:
                        self.instance.dynamic_answers.add(DynamicNolleFormQuestionAnswer.objects.get(pk=pk))

    def get_form_helper(self, form_tag=True):
        helper = super().get_form_helper(form_tag)
        helper.layout = Layout(
            Fieldset(
                "Om dig",
                Row(
                    Column(Field('first_name', placeholder="Förnamn")),
                    Column(Field('last_name', placeholder="Efternamn"))
                ),
                Row(
                    Column(Field('nick_name', placeholder="Smeknamn")), Column(),
                ),
                Row(
                    Column(Field('age', placeholder="Ålder")),
                    Column(Field('age_feeling', placeholder='"Egentlig ålder"'))
                ),
                Row(
                    Column(Field('home_address', placeholder="Adress")),
                    Column(Field('phone_number', placeholder="Mobilnummer"))
                ),
            ),
            Fieldset(
                "Anhöriginformation",
                HTML('<p>Om något oväntat skulle hända kan det vara bra för oss att ha någon att kontakta.</p>'
                     '<br>'),
                Row(
                    Column(Field('contact_name', placeholder="Namn"), css_class='col-md-4'),
                    Column(Field('contact_relation', placeholder="Relation"), css_class='col-md-4'),
                    Column(Field('contact_phone_number', placeholder="Mobilnummer"), css_class='col-md-4')
                ),
            ),
            Fieldset(
                "Information till evenemang",
                'food_preference'
            ),
            Fieldset(
                "Fler frågor!?",
                *[self._get_dynamic_questions_layout(question) for question in DynamicNolleFormQuestion.objects.all()]
            ),
            Fieldset(
                "Övrigt",
                'other',
                'about_the_form'
            ),
        )
        return helper

    def _get_dynamic_questions_layout(self, question):
        return Field('q_' + str(question.pk))
