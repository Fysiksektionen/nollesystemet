from django.apps import apps
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView


import nollesystemet.models as models
import nollesystemet.forms as forms
import nollesystemet.mixins as mixins
from .misc import ModifiableModelFormView, ObjectsAdministrationListView


class ProfilePageView(mixins.FadderietMixin, ModifiableModelFormView):
    model = models.UserProfile
    form_class = forms.ProfileUpdateForm
    deletable = False
    submit_name = "Spara"
    exclude_fields = ('nolle_group', 'user_type', 'groups')

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


class UsersListView(mixins.FohserietMixin, ObjectsAdministrationListView):
    model = models.UserProfile
    template_name = 'fohseriet/anvandare/index.html'

    ordering = 'first_name'

    form_class = forms.UserAdministrationForm

    login_required = True

    def test_func(self):
        return models.UserProfile.can_see_some_user(self.request.user.profile)

    def get_queryset(self):
        self.queryset = models.UserProfile.objects.all()
        querryset = super().get_queryset()
        querryset = [user for user in querryset if user.can_see(self.request.user.profile)]
        return [{
            'user': user,
            'can_edit': user.can_edit(self.request.user.profile),
            'can_see_registrations': user.can_see_registration(self.request.user.profile),
            'form': forms.ProfileUpdateForm(instance=user, editable=False)
        } for user in querryset]

    def get_context_data(self, **kwargs):
        if not self.request.user.profile.has_perm('nollesystemet.edit_user'):
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
        for user_info in file_data:
            try:
                user = models.UserProfile.create_new_user(**user_info)
                users.append(user)
            except ValidationError as e:
                errors.append("Fel vid skapande av användare '%s': %s" % (
                    user_info['first_name'] + ' ' + user_info['last_name'], ", ".join(e.messages)
                ))

        self.file_upload_information = ""
        self.file_upload_success = True

        if errors:
            self.file_upload_success = False
            self.file_upload_information += "\n".join(errors)
        if users:
            self.file_upload_information += "Följande användare laddes upp: %s" % (
                ", ".join([user.name for user in users])
            )

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
            return self.object.can_edit(self.request.user.profile)
        else:
            return False

    def get_is_editable_args(self):
        return [self.request.user.profile]

    def get_object(self, queryset=None):
        if 'pk' not in self.kwargs:
            return None
        return super().get_object(queryset=queryset)


class UserRegistrationsListView(mixins.FohserietMixin, ListView):
    model = models.Registration
    template_name = 'fohseriet/anvandare/anmalningar.html'

    login_required = True
    permission_required = 'nollesystemet.edit_user_info'

    back_url = reverse_lazy('fohseriet:anvandare:index')

    def query_test_func(self, registration):
        return self.request.user.has_perm(
            'nollesystemet.edit_user_registration') or self.request.user.profile in registration.happening.editors.all()

    def get_queryset(self):
        try:
            self.queryset = models.Registration.objects.filter(user=models.UserProfile.objects.get(pk=self.kwargs['pk']))
            return [{'registration': registration, 'user_can_edit': self.query_test_func(registration)} for registration
                    in super().get_queryset()]
        except:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'user_of_registrations': models.UserProfile.objects.get(pk=self.kwargs['pk']),
        })
        return context
