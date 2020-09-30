import django.forms as forms
from crispy_forms.layout import Submit, Layout, Row, Column, HTML, Field
from django.forms import widgets

from nollesystemet.models import Registration, UserProfile, ExtraOption, DrinkOption
from .misc import ModifiableModelForm, _blank_fields_crispy

import logging
logger = logging.getLogger(__name__)

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

    def __init__(self, happening=None, user=None, observing_user=None, **kwargs):
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
        if self.happening.drinkoption_set.count() > 0:
            self.fields['drink_option'].queryset = self.happening.drinkoption_set.all().order_by('price')
            self.fields['drink_option'].required = True
        else:
            self.fields['drink_option'].queryset = DrinkOption.objects.none()

        if self.happening.extraoption_set.count() > 0:
            self.fields['extra_option'].queryset = self.happening.extraoption_set.all().order_by('price')
        else:
            self.fields['extra_option'].queryset = ExtraOption.objects.none()

    def update_nonused_fields(self):
        layout_exclude = []
        if not self.happening.food:
            self.fields.pop('food_preference')
            layout_exclude.append('food_preference')
        if len(self.fields['drink_option'].queryset) == 0:
            self.fields.pop('drink_option')
            layout_exclude.append('drink_option')
        if len(self.fields['extra_option'].queryset) == 0:
            self.fields.pop('extra_option')
            layout_exclude.append('extra_option')

        _blank_fields_crispy(self.helper.layout, layout_exclude)

    def get_form_helper(self, form_tag=True):
        helper = super().get_form_helper(form_tag)
        helper.layout = Layout(
            'food_preference',
            'drink_option',
            'extra_option',
            'other'
        )
        return helper

    def append_submits(self):
        """ Appends the correct configuration of submit buttons to self.helper.layout. """
        if self.is_editable:
            if self.helper.form_tag:
                self.helper.layout.fields.append(
                    Row(
                        Column(HTML(self.submit_button), css_class="d-flex justify-content-start"),
                        Column(HTML("""<button type="submit" name="confirmmail" class="btn btn-primary" id="submit-id-confirmmail">
                                       """ + "Skicka bekräftelse" + """ <i class="fa fa-refresh" aria-hidden="true"></i>
                                   </button>""" if (self.is_deletable and self.instance.pk) else ""),
                               css_class="d-flex justify-content-center"),
                        Column(HTML(self.delete_button if self.is_deletable else ""),
                               css_class="d-flex justify-content-end")
                    )
                )

    def save(self, commit=True):
        if self.is_new:
            self.instance.happening = self.happening
            self.instance.user = self.user

        registration = super().save(commit)
        if self.is_new:
            if self.instance.user.user_type in UserProfile.UserType.list_parse(self.happening.automatic_confirmation):
                msg = ""
                try:
                    failed = not registration.send_confirmation_email()
                except Exception as e:
                    failed = True
                    msg = str(e)
                    print(msg)
                if failed:
                    logger.exception("Fel när %s skulle få bekräftelse till %s. Fel: %s" %(str(self.user), str(self.happening), msg))

        return registration


