import csv
from io import StringIO

import django.forms as forms
from django.apps import apps
from django.conf import settings

from crispy_forms.bootstrap import UneditableField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field, Row, Column, HTML
from django.contrib.auth import password_validation
from django.contrib.auth.forms import PasswordResetForm as AuthPasswordResetForm
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.db.models import Q

from nollesystemet.models import UserProfile, NolleGroup
from .misc import ExtendedMetaModelForm, ModifiableModelForm, MultipleModelsModifiableForm, CsvFileAdministrationForm


class PasswordResetForm(AuthPasswordResetForm):
    def get_users(self, email):
        users = super(PasswordResetForm, self).get_users(email)
        return [user for user in users if user.has_usable_password()]


class AuthUserUpdateForm(ModifiableModelForm):
    confirm_email_address = forms.EmailField()
    confirm_password = forms.CharField()

    class Meta:
        model = apps.get_model(settings.AUTH_USER_MODEL)
        fields = ['username', 'email', 'password']
        field_args = {
            'username': {
                'label': 'Användarnamn',
                'required': False,
                'disabled': True,
                'help_text': None
            },
            'email': {
                'label': 'Epostadress',
                'required': True
            },
            'confirm_email_address': {
                'label': 'Bekräfta epostadress',
                'required': False,
            },
            'password': {
                'label': 'Lösenord',
                'required': False,
                'help_text': "Lämna tom om personen endast ska kunna logga in med KTH-id.",
                'widget_class': forms.PasswordInput,
                'widget_attrs': {'autocomplete': 'new-password'},
                'strip': False,
            },
            'confirm_password': {
                'label': 'Bekräfta lösenord',
                'required': False,
                'widget_class': forms.PasswordInput,
                'widget_attrs': {'autocomplete': 'new-password'},
                'strip': False,
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.is_new:
            self.fields['username'].disabled = False
            self.fields['username'].required = True
            self.fields.pop('confirm_email_address')
        else:
            self.fields.pop('password')
            self.fields.pop('confirm_password')

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset("Inloggningsdetaljer",
                     Row(Column(Field('username'), css_class="col-6")),
                     Row(Column(Field('email')), Column(Field('confirm_email_address', placeholder="Bekräfta epostadress"))),
                     Row(Column(Field('password')), Column(Field('confirm_password')))
                     )
        )
        if self.is_editable and self.instance.pk is not None and self.instance.can_set_password:
            self.helper.layout.fields[0].append(
                HTML("<a href='{{ change_password_url }}' class='btn btn-primary'>Byt lösenord</a>")
            )

    def get_is_editable(self, observing_user=None):
        if observing_user is not None:
            return self.instance == observing_user.auth_user or self.instance.pk is None
        else:
            return False

    def clean_email(self):
        existing = self._meta.model.objects.filter(email__iexact=self.cleaned_data['email'])
        if existing.exists() and self.instance not in existing:
            raise forms.ValidationError('A user with that email already exists.')
        return self.cleaned_data['email']

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password or confirm_password:
            if password != confirm_password:
                raise forms.ValidationError(
                    "Lösenorden stämmer inte överens.",
                    code='password_mismatch',
                )
            else:
                password_validation.validate_password(confirm_password, self.instance)
        return confirm_password

    def clean(self):
        if 'email' in self.cleaned_data and 'confirm_email_address' in self.cleaned_data:
            if self.cleaned_data['email'] != self.cleaned_data['confirm_email_address']:
                if self.cleaned_data['confirm_email_address'] != "" or self.cleaned_data['email'] != self.instance.email:
                    self.add_error('confirm_email_address', 'Detta fält är inte samma som den angivna mejladdressen. '
                                                            'Lämna blankt för att behålla din nuvarande mejladress.')
        return super().clean()

    def save(self, commit=True):
        if 'password' in self.cleaned_data:
            if self.cleaned_data['password']:
                self.instance.set_password(self.cleaned_data["password"])
            else:
                self.instance.set_unusable_password()
        return super().save(commit=commit)


class AuthUserGroupsUpdateForm(ModifiableModelForm):
    class Meta:
        model = apps.get_model(settings.AUTH_USER_MODEL)
        fields = ['groups']
        field_args = {
            'groups': {
                'label': 'Administratörsegenskaper',
                'widget_class': forms.CheckboxSelectMultiple,
            }
        }

    def get_is_editable(self, observing_user=None):
        if observing_user is not None:
            return self.instance.profile.can_edit_groups(observing_user)
        else:
            return False


class ProfileUpdateForm(MultipleModelsModifiableForm):
    extra_form_classes = [AuthUserUpdateForm, AuthUserGroupsUpdateForm]

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
                'widget_class': forms.widgets.Textarea,
                'widget_attrs': {'rows': 3}
            },
            'kth_id': {
                'required': False,
                'label': 'KTH-id',
            },
            'nolle_group': {
                'label': 'nØllegrupp',
            },
            'user_type': {
                'label': 'Användartyp',
            },
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if self.instance.user_type == UserProfile.UserType.NOLLAN:
            self.fields.pop('kth_id')
            self.helper.layout.fields[1].fields[1].fields[1].pop(0)

        if 'exclude_fields' in kwargs and kwargs['exclude_fields'] is not None:
            for field_name in ['nolle_group', 'user_type', 'groups']:
                if field_name not in kwargs['exclude_fields']:
                    break
            else:
                self.helper.layout.fields.pop(4)
            for field_name in ['username', 'email', 'confirm_email_address']:
                if field_name not in kwargs['exclude_fields']:
                    break
            else:
                self.helper.layout.fields.pop(0)

    def get_is_editable(self, observing_user=None):
        if observing_user is not None:
            return self.instance.can_edit(observing_user)
        else:
            return False

    def late_get_form_helper(self, form_tag=None):
        helper = super().late_get_form_helper(form_tag)
        helper.layout = Layout(
            *self.extra_forms[0].helper.layout.fields,
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
            Fieldset("Grupptillhörigheter",
                         Row(
                             Column(Field('nolle_group')),
                             Column(Field('user_type')),
                             Column(Field('groups'))
                         )
                     )
        )
        return helper

    def get_extra_instances(self):
        auth_user = None
        try:
            auth_user = self.instance.auth_user
        except:
            pass
        if auth_user is None:
            auth_user = apps.get_model(settings.AUTH_USER_MODEL)()
            self.instance.auth_user = auth_user
        return [auth_user, auth_user]


class UserAdministrationForm(CsvFileAdministrationForm):
    model = UserProfile
    verbose_name_singular = "Användare"
    verbose_name_plural = "Användare"

    form_tag = True

    create_object_url = reverse_lazy('fohseriet:anvandare:skapa')

    file_columns = ['username', 'email', 'password',
                    'user_type', 'first_name', 'last_name', 'program', 'kth_id', 'phone_number', 'nolle_group']

    required_columns = ['username', 'email', 'user_type', 'first_name', 'last_name']
    val_or_none_columns = ['password', 'program', 'nolle_group']
    val_or_blank_str_columns = ['kth_id', 'phone_number']

    enum_columns = [('user_type', UserProfile.UserType, False), ('program', UserProfile.Program, False)]
    object_columns = [('nolle_group', NolleGroup, True)]

    can_create = True
    can_delete = True
    can_upload = True
    can_download = False

    def delete_all(self):
        UserProfile.objects.filter(~Q(user_type=UserProfile.UserType.ADMIN)).delete()