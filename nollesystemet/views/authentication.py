import django.contrib.auth.views as django_auth_views
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
import django.contrib.auth as django_auth

import authentication.views as auth_views

import nollesystemet.forms as forms
import nollesystemet.mixins as mixins
import nollesystemet.models as models


class LoginViewFohseriet(mixins.FohserietMixin, auth_views.login.Login):
    default_redirect_url = reverse_lazy('fohseriet:index')
    template_name = 'fohseriet/logga-in/index.html'
    cred_login_url = reverse_lazy('fohseriet:logga-in:cred')
    cas_login_url = reverse_lazy('fohseriet:logga-in:cas')


class LoginViewFadderiet(mixins.FadderietMixin, auth_views.login.Login):
    default_redirect_url = reverse_lazy('fadderiet:index')
    template_name = 'fadderiet/logga-in/index.html'
    cred_login_url = reverse_lazy('fadderiet:logga-in:nollan')
    cas_login_url = reverse_lazy('fadderiet:logga-in:fadder')


class LogoutViewFohseriet(mixins.FohserietMixin, django_auth_views.LogoutView):
    next_page = reverse_lazy('fadderiet:index')


class LogoutViewFadderiet(mixins.FadderietMixin, django_auth_views.LogoutView):
    next_page = reverse_lazy('fadderiet:index')


class LoginCredentialsViewFohseriet(mixins.FohserietMixin, auth_views.login.LoginCred):
    template_name = 'fohseriet/logga-in/cred.html'
    default_redirect_url = reverse_lazy('fohseriet:index')

    form_class = forms.make_form_crispy(auth_views.login.LoginCred.form_class, 'Logga in')

    extra_context = {
        'reset_password_url': reverse_lazy('fadderiet:aterstall-losenord:index'),
    }


class LoginCredentialsViewFadderiet(mixins.FadderietMixin, auth_views.login.LoginCred):
    template_name = 'fadderiet/logga-in/nollan.html'
    default_redirect_url = reverse_lazy('fadderiet:index')

    form_class = forms.make_form_crispy(auth_views.login.LoginCred.form_class, 'Logga in')

    extra_context = {
        'reset_password_url': reverse_lazy('fadderiet:aterstall-losenord:index'),
    }


class RegisterView(mixins.FadderietMixin, auth_views.user.AuthUserCreateView):
    template_name = 'fadderiet/registrera-dig.html'
    success_url = reverse_lazy('fadderiet:logga-in:index')

    form_class = forms.make_form_crispy(auth_views.user.AuthUserCreateView.form_class, 'Registrera')

    def get_initial(self):
        initial = super().get_initial()
        initial.update({
            'user_type': models.UserProfile.UserType.NOLLAN
        })


class PasswordChangeView(mixins.FadderietMixin, auth_views.password.PasswordChangeView):
    success_url = reverse_lazy('fadderiet:byt-losenord:klart')
    template_name = 'fadderiet/byt-losenord/index.html'
    form_class = forms.make_form_crispy(auth_views.password.PasswordChangeView.form_class, submit_button='Byt lösenord')

    def test_func(self):
        return self.request.user.has_usable_password()


class PasswordChangeDoneView(mixins.FadderietMixin, auth_views.password.PasswordChangeDoneView):
    template_name = 'fadderiet/byt-losenord/klart.html'

    def test_func(self):
        return self.request.user.has_usable_password()


class PasswordResetView(mixins.FadderietMixin, auth_views.password.PasswordResetView):
    email_template_name = 'fadderiet/aterstall-losenord/epost.txt'
    html_email_template_name = 'fadderiet/aterstall-losenord/epost.html'
    subject_template_name = 'fadderiet/aterstall-losenord/epost-amne.txt'
    success_url = reverse_lazy('fadderiet:aterstall-losenord:skickat')
    template_name = 'fadderiet/aterstall-losenord/index.html'
    form_class = forms.make_form_crispy(auth_views.password.PasswordResetView.form_class, submit_button='Återställ lösenord')


class PasswordResetDoneView(mixins.FadderietMixin, auth_views.password.PasswordResetDoneView):
    template_name = 'fadderiet/aterstall-losenord/skickat.html'


class PasswordResetConfirmView(mixins.FadderietMixin, auth_views.password.PasswordResetConfirmView):
    template_name = 'fadderiet/aterstall-losenord/lank.html'
    success_url = reverse_lazy('fadderiet:aterstall-losenord:klart')
    form_class = forms.make_form_crispy(auth_views.password.PasswordResetConfirmView.form_class, submit_button='Sätt nytt lösenord')


class PasswordResetCompleteView(mixins.FadderietMixin, auth_views.password.PasswordResetCompleteView):
    template_name = 'fadderiet/aterstall-losenord/klart.html'
    extra_context = {'login_url': reverse_lazy('fadderiet:logga-in:index')}

