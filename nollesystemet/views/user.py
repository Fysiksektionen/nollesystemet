from django.apps import apps
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView


import nollesystemet.models as models
import nollesystemet.forms as forms
import nollesystemet.mixins as mixins
from .misc import MultipleObjectsUpdateView


class ProfilePageView(LoginRequiredMixin, mixins.FadderietMenuMixin, MultipleObjectsUpdateView):
    model_list = [apps.get_model(settings.AUTH_USER_MODEL), apps.get_model(settings.USER_PROFILE_MODEL)]
    form_class_list = [forms.AuthUserUpdateForm, forms.ProfileUpdateForm]

    template_name = 'fadderiet/mina-sidor/profil.html'
    success_url = reverse_lazy('fadderiet:mina-sidor:profil')

    extra_context = {
        'change_password_url': reverse_lazy('fadderiet:byt-losenord:index')
    }

    def get_objects(self):
        return self.request.user, self.request.user.profile

    def form_valid(self, forms):
        self.request.user.profile.has_set_profile = True
        return super().form_valid(forms)

    def get_success_url(self):
        if REDIRECT_FIELD_NAME in self.request.GET:
            return self.request.GET[REDIRECT_FIELD_NAME]
        else:
            return super().get_success_url()


class UsersListView(LoginRequiredMixin, PermissionRequiredMixin, mixins.FohserietMenuMixin, ListView):
    model = apps.get_model(settings.USER_PROFILE_MODEL)
    template_name = 'fohseriet/anvandare/index.html'

    permission_required = "fohseriet.edit_user_info"

    extra_context = {
        'user_groups': apps.get_model('authentication.UserGroup').objects.filter(is_external=False),
        'nolle_groups': apps.get_model('authentication.NolleGroup').objects.all()
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'user_can_edit_user_info': self.request.user.has_perm('fohseriet.edit_user_info'),
            'user_can_edit_registrations': self.request.user.has_perm(
                'fohseriet.edit_user_registration') or models.Happening.objects.filter(
                editors=self.request.user.profile.pk).count() > 0
        })
        return context


class UserUpdateView(LoginRequiredMixin, PermissionRequiredMixin, mixins.FohserietMenuMixin, mixins.RedirectToGETArgMixin, MultipleObjectsUpdateView):
    model_list = [models.UserProfile, apps.get_model(settings.AUTH_USER_MODEL)]
    form_class_list = [forms.ProfileUpdateForm, forms.AuthUserGroupsUpdateForm]

    template_name = 'fohseriet/anvandare/redigera.html'
    success_url = reverse_lazy('fohseriet:anvandare:index')

    permission_required = 'fohseriet.edit_user_info'

    def get_objects(self):
        auth_user = apps.get_model(settings.AUTH_USER_MODEL).objects.get(pk=self.kwargs['pk'])
        return auth_user.profile, auth_user

class UserRegistrationsListView(LoginRequiredMixin, PermissionRequiredMixin, mixins.FohserietMenuMixin, ListView):
    model = models.Registration
    template_name = 'fohseriet/anvandare/anmalningar.html'

    permission_required = 'fohseriet.edit_user_info'

    def query_test_func(self, registration):
        return self.request.user.has_perm(
            'fohseriet.edit_user_registration') or self.request.user.profile in registration.happening.editors.all()

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
            'back_url': reverse('fohseriet:anvandare:index'),
        })
        return context
