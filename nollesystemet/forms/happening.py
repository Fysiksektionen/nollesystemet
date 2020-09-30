from crispy_forms.helper import FormHelper
from django import forms
from django.forms.widgets import Textarea, DateTimeInput

from crispy_forms.layout import Layout, Fieldset, Field, Row, Column, HTML, Div, Submit

import nollesystemet.models as models
from .misc import ModifiableModelForm, custom_inlineformset_factory
from .widgets import BootstrapDateTimePickerInput

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
                'widget_class': forms.CheckboxSelectMultiple,
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
                                [models.UserProfile.UserType.NOLLAN, models.UserProfile.UserType.FADDER]
                                )
        self.initial.setdefault('automatic_confirmation',
                                [models.UserProfile.UserType.NOLLAN, models.UserProfile.UserType.FADDER]
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


class HappeningPaidAndPresenceForm(forms.Form):
    def __init__(self, *args, happening=None, **kwargs):
        if not happening:
            raise Exception("No happening was given to form.")

        super().__init__(*args, **kwargs)

        self.happening = happening
        self.registrations = models.Registration.objects.filter(happening=self.happening).order_by('user__first_name')
        for i, registration in enumerate(self.registrations):
            self.fields['%d_paid' % i] = forms.BooleanField(required=False,
                                                            initial=registration.paid,
                                                            label='Betalat')
            self.fields['%d_attended' % i] = forms.BooleanField(required=False,
                                                                initial=registration.attended,
                                                                label='Närvarar')

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column(HTML('<h5>Användare</h5>')),
                Column(HTML('Pris')),
                Column(HTML('Dryck' if self.happening.drinkoption_set.count() > 0 else '')),
                Column(HTML('Har betalat')),
                Column(HTML('Har deltagit'))
            ),
            *[Row(
                Column(HTML('%s' % str(registration.user))),
                Column(HTML(self.price_HTML(registration))),
                Column(HTML(registration.drink_option.drink if registration.drink_option else '')),
                Column('%d_paid' % i),
                Column('%d_attended' % i)
            ) for i, registration in enumerate(self.registrations)],
            HTML("""<button type="submit" name="submit" class="btn btn-primary" id="submit-id-submit">
                    Spara <i class="fa fa-save" aria-hidden="true"></i>
                    </button>""")
        )

    def update_registrations(self):
        for i, registration in enumerate(self.registrations):
            registration.paid = self.cleaned_data['%d_paid' % i]
            registration.attended = self.cleaned_data['%d_attended' % i]
            registration.save()

    def price_HTML(self, registration):
        if registration.on_site_paid_price:
            return '%s kr (+%s kr)' % (str(registration.pre_paid_price), str(registration.on_site_paid_price))
        else:
            return '%s kr' % str(registration.pre_paid_price)


class HappeningConfirmForm(forms.Form):
    def __init__(self, *args, happening=None, **kwargs):
        if not happening:
            raise Exception("No happening was given to form.")

        super().__init__(*args, **kwargs)

        self.happening = happening
        self.registrations = models.Registration.objects.filter(
            happening=self.happening, confirmed=False
        ).order_by('user__first_name')
        for i, registration in enumerate(self.registrations):
            self.fields['%d_confirmed' % i] = forms.BooleanField(required=False,
                                                                 initial=registration.confirmed,
                                                                 label='',
                                                                 disabled=registration.confirmed)

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column(HTML('<h5>Användare</h5>')),
                Column()
            ),
            *[Row(
                Column(HTML('%s' % str(registration.user))),
                Column('%d_confirmed' % i),
            ) for i, registration in enumerate(self.registrations)],
            HTML("""<button type="submit" name="submit" class="btn btn-primary" id="submit-id-submit">
                    Spara <i class="fa fa-save" aria-hidden="true"></i>
                    </button>""")
        )

    def update_confirmed(self):
        failed_users = []
        for i, registration in enumerate(self.registrations):
            if not registration.confirmed:
                if self.cleaned_data['%d_confirmed' % i]:
                    try:
                        if not registration.send_confirmation_email():
                            failed_users.append(registration.user)
                    except Exception as e:
                        failed_users.append(registration.user)
        return len(failed_users) == 0, failed_users

