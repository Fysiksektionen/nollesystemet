from django import forms
from django.forms.widgets import Textarea, DateTimeInput

from crispy_forms.layout import Layout, Fieldset, Field, Row, Column, HTML

from authentication.models import NolleGroup, UserGroup

from nollesystemet.models import Happening, DrinkOption, ExtraOption, GroupBasePrice
from .misc import CreateSeeUpdateModelForm, custom_inlineformset_factory

class HappeningForm(CreateSeeUpdateModelForm):
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
                'widget': DateTimeInput(),
            },
            'end_time': {
                'label': 'Slut-tid',
                'widget': DateTimeInput(),
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
                'queryset': UserGroup.objects.all().exclude(is_administrational=True)
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

    def __init__(self, **kwargs):
        initial = {
            'user_groups': UserGroup.objects.filter(name__in=['nØllan', 'Fadder']),
            'nolle_groups': NolleGroup.objects.all()
        }
        if 'initial' in kwargs:
            initial.update(kwargs['initial'])
        kwargs['initial'] = initial

        super().__init__(**kwargs)

    def get_is_editable(self, **kwargs):
        return True

    def get_form_helper(self, submit_name=None, form_tag=True):
        helper = super().get_form_helper(submit_name, False)
        helper.layout = Layout(
            Fieldset("Systeminfo",
                     Field('editors', data_live_search="true", css_class="bootstrap-select"),
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
        return helper

GroupBasePriceFormset = custom_inlineformset_factory(
    Happening,
    GroupBasePrice,
    ['group', 'base_price'],
    ['Grupp', 'Baspris'],
    formclass="base-price",
    extra=1,
)
DrinkOptionFormset = custom_inlineformset_factory(
    Happening,
    DrinkOption,
    ['drink', 'price'],
    ['Dryck', 'Pris'],
    formclass="drink-option",
    extra=1,
)
ExtraOptionFormset = custom_inlineformset_factory(
    Happening,
    ExtraOption,
    ['extra_option', 'price'],
    ['Tillval', 'Pris'],
    formclass="extra-option",
    extra=1,
)
