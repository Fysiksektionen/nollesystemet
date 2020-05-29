from django import forms
from django.apps import apps
from django.forms import ModelForm, modelformset_factory, inlineformset_factory
from django.forms.widgets import Textarea

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field, Row, Column, HTML, Button

from authentication.models import NolleGroup, UserGroup
from fohseriet.models import *
from utils.forms import ExtendedMetaModelForm


class HappeningForm(ExtendedMetaModelForm):
    class Meta:
        model = Happening
        exclude = ['image_file_path']
        field_args = {
            'name': {
                'label': 'Eventnamn',
            },
            'description': {
                'label': 'Beskrivning',
                'help_text': 'Bör inte innehålla pris eller tid. Det syns automatiskt efter beskrivningen.',
                'widget': Textarea(attrs={'rows': 5})
            },
            'start_time': {
                'label': 'Start-tid',
                'widget': forms.SelectDateWidget(),
            },
            'end_time': {
                'label': 'Slut-tid',
                'widget': forms.SelectDateWidget(),
            },
            'takes_registration': {
                'label': 'Kräver anmälan',
            },
            'external_registration': {
                'label': 'Accepterar icke-användare',
            },
            'user_groups': {
                'label': 'Välkomna grupper',
                'widget': forms.CheckboxSelectMultiple(),
                'queryset': UserGroup.objects.all().exclude(name__in=['Administratör', 'Arrangör'])
            },
            'nolle_groups': {
                'label': 'Välkomna nØllegrupper',
                'widget': forms.CheckboxSelectMultiple(),
                'help_text': "Välj alla för att välkomna alla grupper."
            },
            'food': {
                'label': 'Serverar mat',
            },
            'editors': {
                'label': 'Eventadministratörer',
            },
        }

    def __init__(self, *args, **kwargs):
        if 'instance' not in kwargs or not kwargs['instance'] or not kwargs['instance'].pk:
            initial = {
                'user_groups': UserGroup.objects.filter(name__in=['nØllan', 'Fadder']),
                'nolle_groups': NolleGroup.objects.all()
            }
            if 'initial' in kwargs:
                initial.update(kwargs['initial'])
            kwargs['initial'] = initial

        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset("Systeminfo",
                     Field('editors'),
                     Row(
                         Column(Field('user_groups')),
                         Column(Field('nolle_groups'))
                     ),
            ),
            HTML("<hr>"),
            Fieldset("Anmälningsinformation",
                     Row(Column(Field('name'), css_class="col-6")),
                     Field('description'),
                     Row(
                         Column(Field('start_time')),
                         Column(Field('end_time'))
                     )

            )
        )


def get_formset_form_helper(input_names, input_placeholders, wrapper_class=None, input_css_class=None, remove_button_css_class=None):
    helper = FormHelper()
    helper.layout = Layout(
        Row(
            *(Column(
                Field(name, placeholder=placeholder, wrapper_class=wrapper_class, css_class=css_class), css_class="col-5")
              for name, placeholder, css_class in zip(input_names, input_placeholders,
                                                      input_css_class if input_css_class else [''] * len(
                                                          input_names))),
            Column(Button(name="Ta bort", value="Ta bort", wrapper_class=wrapper_class,
                          css_class="btn-danger " + remove_button_css_class), css_class="col-2")
        )
    )
    helper.form_tag = False
    return helper

class DrinkOptionForm(ExtendedMetaModelForm):
    class Meta:
        model = DrinkOption
        fields = ['drink', 'price']
        field_args = {
            'drink': {
                'label': '',
            },
            'price': {
                'label': '',
            },
        }

    helper = get_formset_form_helper(['drink', 'price'],
                                     ['Dryck', 'Pris'],
                                     wrapper_class="pr-2 rb-1",
                                     remove_button_css_class="remove-drink-option")


class GroupBasePriceForm(ExtendedMetaModelForm):
    class Meta:
        model = GroupBasePrice
        fields = ['group', 'base_price']
        field_args = {
            'group': {
                'label': '',
            },
            'base_price': {
                'label': '',
            },
        }

    helper = get_formset_form_helper(['group', 'base_price'],
                                     ['Grupp', 'Baspris'],
                                     wrapper_class="pr-2 rb-1",
                                     remove_button_css_class="remove-base-price")

class ExtraOptionForm(ExtendedMetaModelForm):
    class Meta:
        model = ExtraOption
        fields = ['extra_option', 'price']
        field_args = {
            'extra_option': {
                'label': '',
            },
            'price': {
                'label': '',
            },
        }

    helper = get_formset_form_helper(['extra_option', 'price'],
                                     ['Tillval', 'Pris'],
                                     wrapper_class="pr-2 rb-1",
                                     remove_button_css_class="remove-extra-option")

DrinkOptionFormset = inlineformset_factory(
    Happening,
    DrinkOption,
    form=DrinkOptionForm,
    extra=1,
    can_delete=False
)

GroupBasePriceFormset = inlineformset_factory(
    Happening,
    GroupBasePrice,
    form=GroupBasePriceForm,
    extra=1,
    can_delete=False
)

ExtraOptionFormset = inlineformset_factory(
    Happening,
    ExtraOption,
    form=ExtraOptionForm,
    extra=1,
    can_delete=False,
)

class AuthUserGroupsUpdateForm(ExtendedMetaModelForm):
    class Meta:
        model = apps.get_model(settings.AUTH_USER_MODEL)
        fields = ['user_group', 'nolle_group']
        field_args = {
            'user_group': {
                'label': 'Användartyp',
                'widget': forms.CheckboxSelectMultiple(),
            },
            'nolle_group': {
                'label': 'nØllegrupp',
                'widget': forms.RadioSelect(),
                'empty_label': None,
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset("Grupptillhörigheter",
                     Row(Column(Field('user_group')),
                         Column(Field('nolle_group'))
                         ),
                     )
        )