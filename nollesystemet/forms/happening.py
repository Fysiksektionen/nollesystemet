from django import forms
from django.forms.widgets import Textarea, DateTimeInput

from crispy_forms.layout import Layout, Fieldset, Field, Row, Column, HTML, Div

import nollesystemet.models as models
from .misc import ModifiableModelForm, custom_inlineformset_factory

class HappeningForm(ModifiableModelForm):
    takes_registration = forms.TypedChoiceField(
        coerce=lambda x: x == 'True',
        choices=((True, 'Ja'), (False, 'Nej')),
        widget=forms.RadioSelect
    )
    food = forms.TypedChoiceField(
        coerce=lambda x: x == 'True',
        choices=((True, 'Ja'), (False, 'Nej')),
        widget=forms.RadioSelect
    )

    class Meta:
        model = models.Happening
        exclude = ['image_file_path']
        field_args = {
            'name': {
                'label': 'Eventnamn',
            },
            'description': {
                'label': 'Beskrivning',
                'help_text': 'Bör inte innehålla pris eller tid. Det syns automatiskt efter beskrivningen.',
                'widget_class': Textarea,
                'widget_attrs': {'rows': 5}
            },
            'start_time': {
                'label': 'Start-tid',
                'widget_class': DateTimeInput,
            },
            'end_time': {
                'label': 'Slut-tid',
                'widget_class': DateTimeInput,
            },
            'food': {
                'label': 'Serverar mat',
            },
            'takes_registration': {
                'label': 'Kräver anmälan',
                'required': True
            },
            'user_types': {
                'label': 'Välkomna grupper',
                'widget_class': forms.CheckboxSelectMultiple,
            },
            'nolle_groups': {
                'label': 'Välkomna nØllegrupper',
                'widget_class': forms.CheckboxSelectMultiple,
                'help_text': "Välj alla för att välkomna alla grupper."
            },
            'editors': {
                'label': 'Eventadministratörer',
            },
            'status': {
                'label': "Evenemangsstatus",
            }
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.initial.setdefault('user_types', [models.UserProfile.UserType.NOLLAN, models.UserProfile.UserType.FADDER])
        self.initial.setdefault('nolle_groups', models.NolleGroup.objects.all())

    def get_form_helper(self, form_tag=True):
        helper = super().get_form_helper(form_tag=False)
        helper.layout = Layout(
            Fieldset("Systeminfo",
                     Row('takes_registration', css_id="reg-radio-div"),
                     Row('status', css_class="reg-info"),
                     Row(
                         Column(Field('user_types')),
                         Column(Field('nolle_groups')),
                         css_class="reg-info"
                     ),
                     Field('editors', data_live_search="true", css_class="bootstrap-select"),
                     ),
            HTML("<hr>"),
            Fieldset("Evenemangsinformation",
                     Row(Column(Field('name'), css_class="col-6")),
                     Field('description'),
                     Row(
                         Column(Field('start_time')),
                         Column(Field('end_time'))
                     )
                     ),
            Fieldset("Mat",
                     Div(Field('food'), css_class="reg-info"),
                     )
        )
        return helper


GroupBasePriceFormset = custom_inlineformset_factory(
    models.Happening,
    models.UserTypeBasePrice,
    ['user_type', 'price'],
    ['Grupp', 'Baspris'],
    extra=1,
)
DrinkOptionFormset = custom_inlineformset_factory(
    models.Happening,
    models.DrinkOption,
    ['drink', 'price'],
    ['Dryck', 'Pris'],
    extra=1,
)
ExtraOptionFormset = custom_inlineformset_factory(
    models.Happening,
    models.ExtraOption,
    ['extra_option', 'price'],
    ['Tillval', 'Pris'],
    extra=1,
)
