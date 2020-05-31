from django import forms
from django.forms import inlineformset_factory
from django.forms.widgets import Textarea

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field, Row, Column, HTML

from authentication.models import NolleGroup, UserGroup

from nollesystemet.models import Happening, DrinkOption, ExtraOption, GroupBasePrice
from .misc import get_formset_form_helper, ExtendedMetaModelForm

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
                     ),
                     Field('food'),
            )
        )


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


DrinkOptionFormset = inlineformset_factory(
    Happening,
    DrinkOption,
    form=DrinkOptionForm,
    extra=1,
    can_delete=False
)


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


GroupBasePriceFormset = inlineformset_factory(
    Happening,
    GroupBasePrice,
    form=GroupBasePriceForm,
    extra=1,
    can_delete=False
)


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


ExtraOptionFormset = inlineformset_factory(
    Happening,
    ExtraOption,
    form=ExtraOptionForm,
    extra=1,
    can_delete=False,
)