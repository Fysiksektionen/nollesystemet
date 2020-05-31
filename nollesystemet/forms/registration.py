import django.forms as forms
from django.forms import widgets

from nollesystemet.models import Registration
from utils.forms import ExtendedMetaModelForm


class RegistrationForm(ExtendedMetaModelForm):
    class Meta:
        model = Registration
        fields = ['food_preference', 'drink_option', 'extra_option', 'other']

        field_args = {
            'food_preference': {
                'label': 'Specialkost',
                'required': False,
                'help_text': 'Om du har fyllt i speckost i din profil ser du det här. ',
            },
            'drink_option': {
                'label': 'Dryck',
                'required': False,
                'widget': forms.RadioSelect(),
                'empty_label': None,
            },
            'extra_option': {
                'label': 'Extra val',
                'required': False,
                'widget': forms.CheckboxSelectMultiple(),
            },
            'other': {
                'label': 'Övrigt',
                'required': False,
                'widget': widgets.Textarea(attrs={'rows': 4}),
            },
        }

    def __init__(self, happening=None, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            instance_is_filled = self.instance.user is not None and self.instance.happening is not None
            self.user = self.instance.user
            self.happening = self.instance.happening
        except:
            self.user = user
            self.happening = happening

        if self.happening is None or self.user is None:
            raise Exception('Registration form must be given an instance or both a happening and a user.')

        self.fields['drink_option'].queryset = self.happening.drinkoption_set.all()
        if len(self.fields['drink_option'].queryset) > 0:
            self.fields['drink_option'].required = True
        else:
            self.fields.pop('drink_option')

        self.fields['extra_option'].queryset = self.happening.extraoption_set.all()
        if len(self.fields['extra_option'].queryset) == 0:
            self.fields.pop('extra_option')

        if not self.happening.food:
            self.fields.pop('food_preference')

    def save(self, commit=True):
        self.instance.happening = self.happening
        self.instance.user = self.user
        return super().save(commit)
