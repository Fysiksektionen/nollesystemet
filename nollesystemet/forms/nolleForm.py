from crispy_forms.helper import FormHelper
from django import forms
from crispy_forms.layout import Layout, Fieldset, Field, Row, Column, HTML, Submit, Div

from .misc import CreateSeeUpdateModelForm
from nollesystemet.models import NolleFormAnswer, DynamicQuestion, DynamicAnswer, QuestionType


class NolleFormFileUploadForm(forms.Form):
    nolle_form_file = forms.FileField(label='nØlleformulärets fil',
                                      required=True,
                                      allow_empty_file=False,
                                      help_text="Här laddar du upp en fil som uppdaterar innehållet i nØlleformuläret.")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'nolle_form_file',
            Submit('submit', 'Uppdatera formulär')
        )
        self.helper.form_method = 'post'

class DynamicQuestionCharField(forms.CharField):
    def __init__(self, question, **kwargs):
        self.question = question
        super().__init__(**kwargs)

    def clean(self, value):
        cleaned_value = super().clean(value)
        try:
            return DynamicAnswer.objects.get(question=self.question, value=cleaned_value)
        except DynamicAnswer.DoesNotExist:
            return DynamicAnswer(question=self.question, value=cleaned_value)


class NolleFormBaseForm(CreateSeeUpdateModelForm):
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
                'widget': forms.widgets.Textarea(attrs={'rows': 3})
            },
            'other': {
                'label': 'Övrigt',
                'widget': forms.widgets.Textarea(attrs={'rows': 3})
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
        for question in DynamicQuestion.objects.all():
            if question.question_type == QuestionType.TEXT:
                self.fields['q_' + str(question.pk)] = DynamicQuestionCharField(
                    question,
                    max_length=DynamicAnswer._meta.get_field('value').max_length,
                    widget=forms.Textarea(attrs={"rows": 2})
                )
                if not self.is_new:
                    self.initial['q_' + str(question.pk)] = self.instance.dynamic_answers.get(question=question).value
            elif question.question_type == QuestionType.RADIO:
                self.fields['q_' + str(question.pk)] = forms.ChoiceField(
                    choices=[(str(q.pk), str(q.value)) for q in question.dynamicanswer_set.all()],
                    widget=forms.RadioSelect
                )
                if not self.is_new:
                    self.initial['q_' + str(question.pk)] = self.instance.dynamic_answers.get(question=question).pk
            elif question.question_type == QuestionType.CHECK:
                self.fields['q_' + str(question.pk)] = forms.MultipleChoiceField(
                    choices=[(str(q.pk), str(q.value)) for q in question.dynamicanswer_set.all()],
                    widget=forms.CheckboxSelectMultiple
                )
                if not self.is_new:
                    pks = list(self.instance.dynamic_answers.filter(question=question).values_list('pk'))
                    self.initial['q_' + str(question.pk)] = [str(tup[0]) for tup in pks]
            self.fields['q_' + str(question.pk)].label = '<strong>' + question.number_label + '</strong>. ' + question.title


    def save(self, commit=True):
        super().save(commit=commit)
        for field_name in self.fields:
            if field_name[:2] == 'q_':
                question = DynamicQuestion.objects.get(pk=field_name[2:])

                if question.question_type == QuestionType.TEXT:
                    self.cleaned_data[field_name].save()
                    self.instance.dynamic_answers.add(self.cleaned_data[field_name])
                elif question.question_type == QuestionType.RADIO:
                    self.instance.dynamic_answers.add(DynamicAnswer.objects.get(pk=self.cleaned_data[field_name]))
                elif question.question_type == QuestionType.CHECK:
                    for pk in self.cleaned_data[field_name]:
                        self.instance.dynamic_answers.add(DynamicAnswer.objects.get(pk=pk))


    def get_form_helper(self, submit_name=None, form_tag=True):
        helper = super().get_form_helper(submit_name, form_tag)
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
                *[self._get_dynamic_questions_layout(question) for question in DynamicQuestion.objects.all()]
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