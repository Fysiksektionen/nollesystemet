import django.contrib.auth.views as django_auth_views
from django.apps import apps
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

import authentication.views as auth_views
import fadderiet.forms as forms
import fadderiet.utils as utils
from fadderiet.helper_views import MenuView, MultipleObjectsUpdateView, MenuMixin


class LoginView(MenuView, auth_views.Login):
    default_redirect_url = reverse_lazy('fadderiet:index')
    template_name = 'fadderiet/logga-in/index.html'
    cred_login_url = reverse_lazy('fadderiet:logga-in:nollan')
    cas_login_url = reverse_lazy('fadderiet:logga-in:fadder')


class LogoutView(MenuView, django_auth_views.LogoutView):
    template_name = 'fadderiet/utloggad.html'


class LoginCredentialsView(MenuView, auth_views.LoginCred):
    template_name = 'fadderiet/logga-in/nollan.html'
    default_redirect_url = reverse_lazy('fadderiet:index')

    form_class = utils.make_crispy_form(auth_views.LoginCred.form_class, 'Logga in')

    extra_context = {
        'reset_password_url': reverse_lazy('fadderiet:aterstall-losenord:index'),
        'register_url': reverse_lazy('fadderiet:registrera-dig')
    }


class RegisterView(MenuView, auth_views.AuthUserCreateView):
    template_name = 'fadderiet/registrera-dig.html'
    success_url = reverse_lazy('fadderiet:logga-in:index')

    form_class = utils.make_crispy_form(auth_views.AuthUserCreateView.form_class, 'Registrera')


class PasswordChangeView(MenuView, auth_views.PasswordChangeView):
    success_url = reverse_lazy('authentication:password_change_done')
    template_name = 'fadderiet/byt-losenord/index.html'
    form_class = utils.make_crispy_form(auth_views.PasswordChangeView.form_class, submit_button='Byt lösenord')

class PasswordChangeDoneView(MenuView, auth_views.PasswordChangeDoneView):
    template_name = 'fadderiet/byt-losenord/klart.html'

class PasswordResetView(MenuView, auth_views.PasswordResetView):
    email_template_name = 'fadderiet/aterstall-losenord-epost.html'
    subject_template_name = 'fadderiet/aterstall-losenord-epost-amne.txt'
    success_url = reverse_lazy('fadderiet:aterstall-losenord:skickat')
    template_name = 'fadderiet/aterstall-losenord/index.html'
    form_class = utils.make_crispy_form(auth_views.PasswordResetView.form_class, submit_button='Återställ lösenord')

class PasswordResetDoneView(MenuView, auth_views.PasswordResetDoneView):
    template_name = 'fadderiet/aterstall-losenord/skickat.html'

class PasswordResetConfirmView(MenuView, auth_views.PasswordResetConfirmView):
    template_name = 'fadderiet/aterstall-losenord/lank.html'
    success_url = reverse_lazy('fadderiet:aterstall-losenord:klart')
    form_class = utils.make_crispy_form(auth_views.PasswordResetConfirmView.form_class, submit_button='Sätt nytt lösenord')

class PasswordResetCompleteView(MenuView, auth_views.PasswordResetCompleteView):
    template_name = 'fadderiet/aterstall-losenord/klart.html'
    extra_context = {'login_url': reverse_lazy('fadderiet:logga-in:index')}


class ProfilePageView(LoginRequiredMixin, MenuMixin, MultipleObjectsUpdateView):
    menu_item_info = MenuView.menu_item_info
    menu_items = MenuView.menu_items

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
