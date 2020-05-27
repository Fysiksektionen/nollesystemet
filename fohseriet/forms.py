from django import forms
from django.apps import apps
from django.forms import ModelForm, modelformset_factory, inlineformset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field, Row, Column, HTML

from .models import *
from utils.forms import ExtendedMetaModelForm


class HappeningForm(ModelForm):
    class Meta:
        model = Happening
        exclude = ['image_file_path']


DrinkOptionFormset = inlineformset_factory(
    Happening,
    DrinkOption,
    fields=['drink', 'price'],
    extra=1,
    can_delete=False)

GroupHappeningPropertiesFormset = inlineformset_factory(
    Happening,
    GroupBasePrice,
    fields=['group', 'base_price'],
    extra=1,
    can_delete=False
)

ExtraOptionFormset = inlineformset_factory(
    Happening,
    ExtraOption,
    fields=['extra_option', 'price'],
    extra=1,
    can_delete=False
)


class AuthUserGroupsUpdateForm(ExtendedMetaModelForm):
    class Meta:
        model = apps.get_model(settings.AUTH_USER_MODEL)
        fields = ['user_group', 'nolle_group']
        field_args = {
            'user_group': {
                'label': 'Användartyp',
            },
            'nolle_group': {
                'label': 'nØllegrupp',
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