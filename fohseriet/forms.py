from django import forms
from django.forms import ModelForm, modelformset_factory, inlineformset_factory
from .models import *


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
    GroupHappeningProperties,
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