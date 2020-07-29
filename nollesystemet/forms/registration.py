import django.forms as forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from django.core.mail import EmailMultiAlternatives
from django.forms import widgets
from django.template import Context
from django.template.loader import get_template
from django.urls import reverse

from nollesystemet.models import Registration
from .misc import ModifiableModelForm


class RegistrationForm(ModifiableModelForm):
    class Meta:
        model = Registration
        fields = ['food_preference', 'drink_option', 'extra_option', 'other']

        field_args = {
            'food_preference': {
                'label': 'Specialkost',
                'required': False,
                'help_text': 'Om du har fyllt i speckost i din profil ser du det här.',
            },
            'drink_option': {
                'label': 'Dryck',
                'required': False,
                'widget_class': forms.RadioSelect,
                'empty_label': None,
            },
            'extra_option': {
                'label': 'Extra val',
                'required': False,
                'widget_class': forms.CheckboxSelectMultiple,
            },
            'other': {
                'label': 'Övrigt',
                'required': False,
                'widget_class': widgets.Textarea,
                'widget_attrs': {'rows': 4, 'disabled': False}
            },
        }

    def __init__(self, happening=None, user=None, observing_user=None, extra_email_context=None, **kwargs):
        if 'instance' not in kwargs:
            if happening is None or user is None:
                kwargs['editable'] = False

        if 'is_editable_args' in kwargs:
            kwargs.pop('is_editable_args')
        super().__init__(is_editable_args=(happening, user, observing_user), **kwargs)

        self.happening = self.instance.happening if not self.is_new else happening
        self.instance.happening = self.happening

        self.user = self.instance.user if not self.is_new else user
        self.instance.user = self.user

        self.observing_user = observing_user
        self.extra_email_context = extra_email_context


        self.update_field_querysets()
        self.update_nonused_fields()

    def delete_instance(self):
        if self.instance.pk is not None:
            self.instance.delete()
        self.__init__(happening=self.happening, user=self.user, observing_user=self.observing_user)

    def get_is_editable(self, happening, user, observing_user, **kwargs):
        enabled = None
        if self.is_new:  # New registration
            if happening is None:  # Error, system does not know what happening to tie the registration to
                ValueError('Instance is None and no happening was given.')
            else:
                if user is None:  # Anonymous registration
                    if observing_user is None:  # Anonymous observer
                        enabled = True
                    else:  # Error, logged in user should register connected to it's profile
                        ValueError('Observing user can not register a registration to an anonymous user.')
                else:
                    if observing_user != user:  # Error, can't register for another user.
                        ValueError('Observing user can not register a registration to another user.')
                    else:
                        enabled = True

        else:  # Existing registration
            if (happening is not None and happening != self.instance.happening) \
                    or (user is not None and user != self.instance.user):  # Error, conflicting information
                ValueError('Instance given and given happening or user is in conflict.')

            if observing_user is not None:  # If an observer is existant
                if self.instance.can_edit(observing_user):  # If it can edit
                    enabled = True
                elif self.instance.can_see(observing_user):  # If it can see
                    enabled = False
                else:  # Not allowed to see
                    ValueError('User may not see the registration.')

            else:  # Anonymous can't edit
                enabled = False

        return enabled

    def update_field_querysets(self):
        self.fields['drink_option'].queryset = self.happening.drinkoption_set.all()
        if len(self.fields['drink_option'].queryset) > 0:
            self.fields['drink_option'].required = True
        else:
            self.fields.pop('drink_option')

        self.fields['extra_option'].queryset = self.happening.extraoption_set.all()
        if len(self.fields['extra_option'].queryset) == 0:
            self.fields.pop('extra_option')

    def update_nonused_fields(self):
        if not self.happening.food:
            self.fields.pop('food_preference')

    def save(self, commit=True):
        if self.is_new:
            self.instance.happening = self.happening
            self.instance.user = self.user

        ret = super().save(commit)
        if self.is_new:
            self._send_confirmation_email()

        return ret

    def _send_confirmation_email(self):
        """ (!) Only call this post save to db. """

        subject_template = get_template('fadderiet/evenemang/bekraftelse_epost_amne.txt')
        plaintext = get_template('fadderiet/evenemang/bekraftelse_epost.txt')
        html = get_template('fadderiet/evenemang/bekraftelse_epost.html')

        if not self.extra_email_context:
            self.extra_email_context = {}

        context = {
            'registration': self.instance,
            'happening': self.instance.happening,
            'user_profile': self.instance.user,
            'form': RegistrationForm(instance=self.instance),
            **self.extra_email_context
        }

        from_email, to = None, str(self.instance.user.email)
        subject = subject_template.render(context)
        text_content = plaintext.render(context)
        html_content = html.render(context)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()


