import django.contrib.auth.views as django_auth_views
from django.urls import reverse_lazy

import authentication.views as auth_views
import fadderiet.utils as fadderiet_utils
import utils.misc as utils_misc

import nollesystemet.mixins as mixins


class LoginViewFohseriet(auth_views.login.Login, mixins.FohserietMenuMixin):
    default_redirect_url = reverse_lazy('fohseriet:index')
    template_name = 'fohseriet/logga-in/index.html'
    cred_login_url = reverse_lazy('fohseriet:logga-in:cred')
    cas_login_url = reverse_lazy('fohseriet:logga-in:cas')


class LoginViewFadderiet(mixins.FadderietMenuMixin, auth_views.login.Login):
    default_redirect_url = reverse_lazy('fadderiet:index')
    template_name = 'fadderiet/logga-in/index.html'
    cred_login_url = reverse_lazy('fadderiet:logga-in:nollan')
    cas_login_url = reverse_lazy('fadderiet:logga-in:fadder')


class LogoutViewFohseriet(django_auth_views.LogoutView, mixins.FohserietMenuMixin):
    template_name = 'fohseriet/utloggad.html'


class LogoutView(mixins.FadderietMenuMixin, django_auth_views.LogoutView):
    template_name = 'fadderiet/utloggad.html'


class LoginCredentialsViewFohseriet(auth_views.login.LoginCred, mixins.FohserietMenuMixin):
    template_name = 'fohseriet/logga-in/cred.html'
    default_redirect_url = reverse_lazy('fohseriet:index')

    form_class = utils_misc.make_crispy_form(auth_views.login.LoginCred.form_class, 'Logga in')


class LoginCredentialsViewFadderiet(mixins.FadderietMenuMixin, auth_views.login.LoginCred):
    template_name = 'fadderiet/logga-in/nollan.html'
    default_redirect_url = reverse_lazy('fadderiet:index')

    form_class = utils_misc.make_crispy_form(auth_views.login.LoginCred.form_class, 'Logga in')

    extra_context = {
        'reset_password_url': reverse_lazy('fadderiet:aterstall-losenord:index'),
        'register_url': reverse_lazy('fadderiet:registrera-dig')
    }


class RegisterView(mixins.FadderietMenuMixin, auth_views.user.AuthUserCreateView):
    template_name = 'fadderiet/registrera-dig.html'
    success_url = reverse_lazy('fadderiet:logga-in:index')

    form_class = fadderiet_utils.make_crispy_form(auth_views.user.AuthUserCreateView.form_class, 'Registrera')


class PasswordChangeView(mixins.FadderietMenuMixin, auth_views.password.PasswordChangeView):
    success_url = reverse_lazy('authentication:password_change_done')
    template_name = 'fadderiet/byt-losenord/index.html'
    form_class = fadderiet_utils.make_crispy_form(auth_views.password.PasswordChangeView.form_class, submit_button='Byt lösenord')


class PasswordChangeDoneView(mixins.FadderietMenuMixin, auth_views.password.PasswordChangeDoneView):
    template_name = 'fadderiet/byt-losenord/klart.html'


class PasswordResetView(mixins.FadderietMenuMixin, auth_views.password.PasswordResetView):
    email_template_name = 'fadderiet/aterstall-losenord-epost.html'
    subject_template_name = 'fadderiet/aterstall-losenord-epost-amne.txt'
    success_url = reverse_lazy('fadderiet:aterstall-losenord:skickat')
    template_name = 'fadderiet/aterstall-losenord/index.html'
    form_class = fadderiet_utils.make_crispy_form(auth_views.password.PasswordResetView.form_class, submit_button='Återställ lösenord')


class PasswordResetDoneView(mixins.FadderietMenuMixin, auth_views.password.PasswordResetDoneView):
    template_name = 'fadderiet/aterstall-losenord/skickat.html'


class PasswordResetConfirmView(mixins.FadderietMenuMixin, auth_views.password.PasswordResetConfirmView):
    template_name = 'fadderiet/aterstall-losenord/lank.html'
    success_url = reverse_lazy('fadderiet:aterstall-losenord:klart')
    form_class = fadderiet_utils.make_crispy_form(auth_views.password.PasswordResetConfirmView.form_class, submit_button='Sätt nytt lösenord')


class PasswordResetCompleteView(mixins.FadderietMenuMixin, auth_views.password.PasswordResetCompleteView):
    template_name = 'fadderiet/aterstall-losenord/klart.html'
    extra_context = {'login_url': reverse_lazy('fadderiet:logga-in:index')}

