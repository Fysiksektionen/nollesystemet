import pandas as pandas
from crispy_forms.helper import FormHelper
from django import forms
from django.forms.widgets import Textarea, DateTimeInput

from crispy_forms.layout import Layout, Fieldset, Field, Row, Column, HTML, Div, Submit

import nollesystemet.models as models
from .misc import ModifiableModelForm, custom_inlineformset_factory
from .widgets import BootstrapDateTimePickerInput
from django.core.exceptions import ValidationError


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

    include_drink_in_price = forms.TypedChoiceField(
        coerce=lambda x: x == 'True',
        choices=((True, 'Ja'), (False, 'Nej')),
        widget=forms.RadioSelect
    )

    include_extra_in_price = forms.TypedChoiceField(
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
                'widget_class': BootstrapDateTimePickerInput,
                'input_formats': ['%d/%m/%Y %H:%M'],
            },
            'end_time': {
                'label': 'Slut-tid',
                'widget_class': BootstrapDateTimePickerInput,
                'input_formats': ['%d/%m/%Y %H:%M'],
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
            },
            'nolle_groups': {
                'label': 'Välkomna nØllegrupper',
                # 'widget_class': forms.CheckboxSelectMultiple,
                'help_text': "Välj alla för att välkomna alla grupper."
            },
            'editors': {
                'label': 'Eventadministratörer',
            },
            'status': {
                'label': "Evenemangsstatus",
            },
            'contact_name': {
                'label': "Namn",
            },
            'contact_phone': {
                'label': "Telefonnummer",
                'required': False
            },
            'contact_email': {
                'label': "E-post",
            },
            'location': {
                'label': 'Plats',
            },
            'include_drink_in_price': {
                'label': 'Inkludera dryckespris i förbetalning',
            },
            'include_extra_in_price': {
                'label': 'Inkludera tillval i förbetalning',
            },
            'exclusive_access': {
                'label': "Exlusiv access",
                'help_text': "Här kan du fylla i folk som ska få access att gå på ett evenemang trots att de inte "
                             "uppfyller grupp-kraven."
            },
            'automatic_confirmation': {
                'label': "Automatiskt bekräftade grupper",
                'help_text': 'Vilka användargrupper som automatiskt får bekräftelsemejl.'
            }

        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.initial.setdefault('user_types',
                                [models.UserProfile.UserType.NOLLAN,
                                 models.UserProfile.UserType.FADDER,
                                 models.UserProfile.UserType.FORFADDER]
                                )
        self.initial.setdefault('automatic_confirmation',
                                [models.UserProfile.UserType.NOLLAN,
                                 models.UserProfile.UserType.FADDER,
                                 models.UserProfile.UserType.FORFADDER]
                                )
        self.initial.setdefault('nolle_groups', models.NolleGroup.objects.all())

    def get_form_helper(self, form_tag=True):
        helper = super().get_form_helper(form_tag=False)
        helper.layout = Layout(
            Fieldset("Systeminfo",
                     Row('takes_registration', css_id="reg-radio-div"),
                     Row('status'),
                     Row(
                         Column(Field('user_types')),
                         Column(Field('nolle_groups')),
                         css_class="reg-info"
                     ),
                     Row(
                         Column(Field('automatic_confirmation')),
                         Column(),
                         css_class="reg-info"
                     ),
                     Field('editors', data_live_search="true", css_class="bootstrap-select"),
                     Field('exclusive_access', data_live_search="true", css_class="bootstrap-select"),
                     ),
            HTML("<hr>"),
            Fieldset("Evenemangsinformation",
                     Row(Column(Field('name'), css_class="col-6")),
                     Field('description'),
                     Row(
                         Column(Field('start_time')),
                         Column(Field('end_time'))
                     ),
                     Field('location'),
                     ),
            Fieldset("Kontaktinformation",
                     Row(Column(
                         'contact_name',
                         'contact_email',
                         'contact_phone',
                         css_class="col-6"
                     ))
                     ),
            Fieldset("Mat",
                     Div(Field('food'), css_class="reg-info"),
                     ),
            Fieldset("Ekonomi",
                     Row(
                         Column(Field('include_drink_in_price')),
                         Column(Field('include_extra_in_price')),
                         css_class="reg-info"
                     )
                     ),
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


class HappeningPaymentUploadForm(forms.Form):
    swish = forms.FileField(required=False)
    bankgiro = forms.FileField(required=False)

    def __init__(self, *args, **kwargs):
        super(HappeningPaymentUploadForm, self).__init__(*args, **kwargs)

        self.fields['swish'].widget.attrs['hidden'] = True
        self.fields['bankgiro'].widget.attrs['hidden'] = True

    def clean_swish(self):
        if 'swish' in self.cleaned_data and self.cleaned_data['swish']:
            try:
                raw_file_content = self.cleaned_data['swish'].read()
                try:
                    file_content = raw_file_content.decode('iso-8859-1')
                except:
                    file_content = raw_file_content.decode('utf-8')

                rows = []
                if '\r' in file_content:
                    rows = file_content.split('\r\n')
                else:
                    rows = file_content.split('\n')

                assert len(rows) > 0
                rows = [row[:-1] for row in rows[1:] if row.strip() != ""]
                rows = [row.split(';') for row in rows]
                return rows

            except Exception as e:
                raise ValidationError("Fel vid avläsning av swish-filen. Har du rätt format på filen?")
        else:
            return None

    def clean_bankgiro(self):
        if 'bankgiro' in self.cleaned_data and self.cleaned_data['bankgiro']:
            try:
                data_frame = pandas.read_excel(self.cleaned_data['bankgiro'].read())

                header_row = 0
                while data_frame.iloc[header_row, 0] != "Avsändare":
                    header_row += 1

                last_row = header_row
                try:
                    while data_frame.iloc[last_row, 0] != "":
                        last_row += 1
                except:
                    last_row -= 1

                rows = [
                    [data_frame.iloc[row, col] for col in [0, 2, 3, 4]]
                    for row in range(header_row + 1, last_row + 1)
                ]

                return rows

            except Exception as e:
                raise ValidationError("Fel vid avläsning av bakgiro-filen. Har du rätt format på filen?: %s" % str(e))

        else:
            return None
