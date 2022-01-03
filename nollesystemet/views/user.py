import sys

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, HttpRequest
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView

import authentication.models as auth_models
import nollesystemet.models as models
import nollesystemet.forms as forms
import nollesystemet.mixins as mixins
from .misc import ModifiableModelFormView, ObjectsAdministrationListView


class ProfilePageView(mixins.FadderietMixin, ModifiableModelFormView):
    model = models.UserProfile
    form_class = forms.ProfileUpdateForm
    deletable = False
    submit_name = "Spara"
    exclude_fields = ['nolle_group', 'user_type', 'groups', 'program']

    template_name = 'fadderiet/mina-sidor/profil.html'
    success_url = reverse_lazy('fadderiet:mina-sidor:profil')

    login_required = True

    extra_context = {
        'change_password_url': reverse_lazy('fadderiet:byt-losenord:index')
    }

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_is_editable_args(self):
        return [self.request.user.profile]

    def get_form_kwargs(self):
        context = super().get_form_kwargs()
        return context


class UsersListView(mixins.FohserietMixin, ObjectsAdministrationListView):
    model = models.UserProfile
    template_name = 'fohseriet/anvandare/index.html'

    ordering = 'first_name'

    form_class = forms.UserAdministrationForm

    login_required = True

    def test_func(self):
        return models.UserProfile.can_see_some_user(self.request.user.profile)

    def get_form_kwargs(self):
        context = super().get_form_kwargs()
        context['can_delete'] = self.request.user.is_superuser
        return context

    def get_queryset(self):
        if self.request.user.is_authenticated:
            self.queryset = models.UserProfile.objects.all()
            querryset = super().get_queryset()
            querryset = [user for user in querryset if user.can_see(self.request.user.profile)]
            return [{
                'user': user,
                'can_see': user.can_see_registrations(self.request.user.profile),
                'can_see_registrations': user.can_see_registrations(self.request.user.profile),
                'can_see_nolleForm': user.can_see_nolleForm_answer(self.request.user.profile),
            } for user in querryset]
        else:
            return []

    def get_context_data(self, **kwargs):
        if not self.request.user.profile.has_perm('nollesystemet.edit_users'):
            kwargs['form'] = None
        context = super().get_context_data(**kwargs)
        context.update({
            'num_of_users_per_type': [
                (user_type.label, models.UserProfile.objects.filter(user_type=user_type).count())
                for user_type in models.UserProfile.UserType
            ],
            'num_of_users_total': models.UserProfile.objects.all().count()
        })
        return context

    def handle_uploaded_file(self, file_data):
        errors = []
        users = []

        all_usernames = auth_models.AuthUser.objects.all().values_list('username', flat=True)
        for user_info in file_data:
            if user_info['username'] in all_usernames:
                user, errors = UsersListView._update_user(user_info, errors)
            else:
                user, errors = UsersListView._create_user(user_info, errors)

            if user:
                users.append(user)

        self.file_upload_information = ""
        self.file_upload_success = True

        if errors:
            self.file_upload_success = False
            self.file_upload_information += "\n".join(errors)
        if users:
            self.file_upload_information += "Följande användare laddes upp: %s" % (
                ", ".join([user.name for user in users])
            )

    @staticmethod
    def _update_user(user_info, errors):
        try:

            return models.UserProfile.update_user(**user_info), errors
        except ValidationError as e:
            errors.append("Fel vid uppdaterande av användare '%s': %s" % (
                user_info['first_name'] + ' ' + user_info['last_name'], ", ".join(e.messages)
            ))
        except:
            errors.append("Fel vid uppdaterande av användare '%s': %s" % (
                user_info['first_name'] + ' ' + user_info['last_name'], "Unexpected error:" + str(sys.exc_info()[0])
            ))

        return None, errors

    @staticmethod
    def _create_user(user_info, errors):
        try:
            return models.UserProfile.create_new_user(**user_info), errors
        except ValidationError as e:
            errors.append("Fel vid skapande av användare '%s': %s" % (
                user_info['first_name'] + ' ' + user_info['last_name'], ", ".join(e.messages)
            ))
        except:
            errors.append("Fel vid skapande av användare '%s': %s" % (
                user_info['first_name'] + ' ' + user_info['last_name'], "Unexpected error:" + str(sys.exc_info()[0])
            ))

        return None, errors

class UserUpdateView(mixins.FohserietMixin, ModifiableModelFormView):
    model = models.UserProfile
    form_class = forms.ProfileUpdateForm
    deletable = True
    submit_name = "Spara"

    template_name = 'fohseriet/anvandare/redigera.html'

    back_url = reverse_lazy('fohseriet:anvandare:index')
    success_url = reverse_lazy('fohseriet:anvandare:index')

    login_required = True

    def test_func(self):
        if not hasattr(self, 'object'):
            self.object = self.get_object()
        if self.object:
            return self.object.can_see(self.request.user.profile)
        else:
            return models.UserProfile.can_create(self.request.user.profile)

    def get_is_editable_args(self):
        return [self.request.user.profile]

    def get_object(self, queryset=None):
        if 'pk' not in self.kwargs:
            return None
        return super().get_object(queryset=queryset)

    def post(self, request, *args, **kwargs):
        """ Alter behaviour if delete is pressed. """
        self.object = self.soft_object_reload()
        if 'resetpassword' in request.POST:
            return self.form_reset_password(self.request, self.object)
        else:
            return super().post(request, *args, **kwargs)

    def form_reset_password(self, request, instance_user):
        reset_failed = False
        reset_failed_message = ""
        try:
            reset_form = forms.PasswordResetForm(data={'email': instance_user.auth_user.email})
            reset_form.is_valid()
            reset_form.save(
                request=request,
                use_https=request.is_secure(),
                email_template_name='fadderiet/aterstall-losenord/epost.txt',
                html_email_template_name='fadderiet/aterstall-losenord/epost.html',
                subject_template_name='fadderiet/aterstall-losenord/epost-amne.txt'
            )
        except Exception as e:
            reset_failed = True
            reset_failed_message = str(e)
        return self.render_to_response(self.get_context_data(reset_failed=reset_failed,
                                                             reset_failed_message=reset_failed_message))

class UserRegistrationsListView(mixins.FohserietMixin, ListView):
    model = models.Registration
    template_name = 'fohseriet/anvandare/anmalningar.html'

    login_required = True

    back_url = reverse_lazy('fohseriet:anvandare:index')

    def setup(self, request, *args, **kwargs):
        super(UserRegistrationsListView, self).setup(request, *args, **kwargs)
        try:
            self.user_of_registrations = models.UserProfile.objects.get(pk=self.kwargs['pk'])
        except models.UserProfile.DoesNotExist:
            self.user_of_registrations = None

    def test_func(self):
        if self.user_of_registrations:
            return self.user_of_registrations.can_see_registrations(self.request.user.profile)
        else:
            return False

    def get_queryset(self):
        try:
            self.queryset = models.Registration.objects.filter(user=self.user_of_registrations)
            return [
                {
                    'registration': registration,
                    'can_edit': registration.can_edit(self.request.user.profile),
                    'form': forms.RegistrationForm(instance=registration, editable=False)
                } for registration in super().get_queryset()
            ]
        except:
            return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'user_of_registrations': self.user_of_registrations,
        })
        return context

class UserNolleFormView(mixins.FohserietMixin, ModifiableModelFormView):
    model = models.NolleFormAnswer
    form_class = forms.NolleFormBaseForm

    editable = False
    form_tag = False

    template_name = 'fohseriet/anvandare/nolleenkaten.html'

    login_required = True

    def test_func(self):
        if self.user_of_answer:
            return self.user_of_answer.can_see(self.request.user.profile)
        else:
            return False

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        try:
            self.user_of_answer = models.UserProfile.objects.get(pk=self.kwargs['pk'])
        except models.UserProfile.DoesNotExist:
            self.user_of_answer = None

        try:
            if self.user_of_answer:
                self.nolle_form_answer = models.NolleFormAnswer.objects.get(user=self.user_of_answer)
            else:
                raise models.NolleFormAnswer.DoesNotExist()
        except models.NolleFormAnswer.DoesNotExist:
            self.nolle_form_answer = None

        self.back_url = reverse('fohseriet:anvandare:index')

    def get_object(self, queryset=None):
        return self.nolle_form_answer

    def get(self, request, *args, **kwargs):
        if self.nolle_form_answer:
            return super().get(request, *args, **kwargs)
        else:
            return self.handle_no_permission()

