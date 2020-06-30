import django.forms as forms
from django.apps import apps
from django.conf import settings

from crispy_forms.bootstrap import UneditableField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field, Row, Column, HTML

from nollesystemet.models import UserProfile
from .misc import ExtendedMetaModelForm, ModifiableModelForm


class AuthUserUpdateForm(ExtendedMetaModelForm):
    confirm_email_address = forms.EmailField()

    class Meta:
        model = apps.get_model(settings.AUTH_USER_MODEL)
        fields = [model.USERNAME_FIELD, 'email']
        field_args = {
            model.USERNAME_FIELD: {
                'disabled': True,
                'label': 'Användarnamn',
            },
            'email': {
                'label': 'Epostadress',
                'required': True
            },
            'confirm_email_address': {
                'label': 'Bekräfta epostadress',
                'required': False,
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset("Inloggningsdetaljer",
                     Row(Column(UneditableField(self._meta.model.USERNAME_FIELD), css_class="col-6")),
                     Row(Column('email'), Column(Field('confirm_email_address', placeholder="Bekräfta epostadress"))),
                     HTML("<a href='{{ change_password_url }}' class='btn btn-primary'>Byt lösenord</a>"),
                     )
        )

    def clean_email(self):
        existing = self._meta.model.objects.filter(email__iexact=self.cleaned_data['email'])
        if existing.exists() and self.instance not in existing:
            raise forms.ValidationError('A user with that email already exists.')
        return self.cleaned_data['email']

    def clean(self):
        if 'email' in self.cleaned_data and 'confirm_email_address' in self.cleaned_data:
            if self.cleaned_data['email'] != self.cleaned_data['confirm_email_address']:
                if self.cleaned_data['confirm_email_address'] != "" or self.cleaned_data['email'] != self.instance.email:
                    self.add_error('confirm_email_address', 'Detta fält är inte samma som den angivna mejladdressen. '
                                                            'Lämna blankt för att behålla din nuvarande mejladress.')

        return super().clean()


class AuthUserGroupsUpdateForm(ExtendedMetaModelForm):
    class Meta:
        model = apps.get_model(settings.AUTH_USER_MODEL)
        fields = ['groups']
        field_args = {
            'groups': {
                'label': 'Administratörsegenskaper',
                'widget': forms.CheckboxSelectMultiple(),
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout('groups')


class ProfileUpdateForm(ModifiableModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'kth_id', 'phone_number', 'food_preference', 'contact_name',
                  'contact_relation', 'contact_phone_number', 'nolle_group', 'user_type']

        field_args = {
            'first_name': {
                'label': 'Förnamn',
                'required': True,
            },
            'last_name': {
                'label': 'Efternamn',
                'required': True,
            },
            'phone_number': {
                'label': 'Mobilnummer',
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
                'widget': forms.widgets.Textarea()
            },
            'kth_id': {
                'required': False,
                'label': 'KTH-id',
            },
            'nolle_group': {
                'label': 'nØllegrupp',
                'widget': forms.RadioSelect(),
                'empty_label': '(Ingen)',
            },
            'user_type': {
                'label': 'Användartyp',
            },
        }

    def __init__(self, *args, observing_user=None, **kwargs):
        print(observing_user)
        super().__init__(*args, is_editable_args=(observing_user,), **kwargs)

        if self.instance.user_type == UserProfile.UserType.NOLLAN:
            self.fields.pop('kth_id')
            self.helper.layout.fields[0].fields[1].fields[1].pop(0)

    def get_is_editable(self, observing_user, **kwargs):
        if observing_user is not None:
            return self.is_new or self.instance.can_edit(observing_user)
        else:
            raise PermissionError("Anonumus user can't access a profile.")

    def get_form_helper(self, submit_name=None, delete_name=None, form_tag=True):
        helper = super().get_form_helper(submit_name, delete_name, form_tag)
        helper.layout = Layout(
            Fieldset("Kontaktupgifter",
                     Row(Column(Field('first_name', placeholder="Förnamn")),
                         Column(Field('last_name', placeholder="Efternamn"))
                         ),
                     Row(Column(Field('phone_number', placeholder="Mobilnummer")),
                         Column(Field('kth_id', placeholder="KTH-id"))
                         )
                     ),
            Fieldset("Anhöriginformation",
                     Row(Column(Field('contact_name', placeholder="Namn"), css_class='col-md-4'),
                         Column(Field('contact_relation', placeholder="Relation"), css_class='col-md-4'),
                         Column(Field('contact_phone_number', placeholder="Mobilnummer"), css_class='col-md-4')
                         ),
                     ),
            Fieldset("Information till evenemang",
                     'food_preference'
                     ),
            Row(
                Column(Field('nolle_group')),
                Column(Field('user_type'))
            ),
        )
        return helper
