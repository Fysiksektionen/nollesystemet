import django.contrib.auth.views as django_auth_views
from django.apps import apps
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import HttpResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import UpdateView
from django.views.generic.base import ContextMixin, TemplateView

import authentication.views as auth_views
import fadderiet.utils as utils


def hello_world(request, *args, **kwargs):
    return HttpResponse("Hello world!\n You are at: " + request.get_full_path_info())


def custom_redirect_view(request, redirect_name, keep_GET_params=True, default_GET_params=None, url_args=None):
    GET_params = default_GET_params
    if not default_GET_params:
        GET_params = {}
    GET_params.update(request.GET)

    if not url_args:
        url_args = []
    if not keep_GET_params or not GET_params:
        GET_params = {}

    return utils.custom_redirect(redirect_name, *url_args, **GET_params)


class MenuBaseMixin(ContextMixin):
    menu_items = []
    menu_item_info = None

    def get_context_data(self, **kwargs):
        if len(self.menu_items) > 0 and not self.menu_item_info:
            raise ReferenceError("menu_item_info not set, with menu_items specified.")

        menu = {'left': [], 'right': []}
        for items in self.menu_items:
            if not isinstance(items, list):
                items = [items]

            for item in items:
                info = self.menu_item_info[item]

                render = info['user'] == 'any' \
                         or (info['user'] == 'logged-in' and self.request.user.is_authenticated) \
                         or (info['user'] == 'logged-out' and not self.request.user.is_authenticated)

                if render:
                    menu[info['align']].append({
                        **info,
                        'url': reverse(info['url_name'])
                    })
                    break

        context = {}
        if menu:
            context['menu'] = menu
        return super().get_context_data(**kwargs, **context)


class MenuBaseView(MenuBaseMixin, TemplateView):
    menu_item_info = utils.menu_item_info
    menu_items = ['index', 'schema', 'bra-info', 'anmal-dig', 'kontakt', ['mina-sidor:profil', 'logga-in'], 'logga-ut']


class LoginView(MenuBaseView, auth_views.Login):
    default_redirect_url = reverse_lazy('fadderiet:index')
    template_name = 'fadderiet/logga-in/index.html'
    cred_login_url = reverse_lazy('fadderiet:logga-in:nollan')
    cas_login_url = reverse_lazy('fadderiet:logga-in:fadder')

class LogoutView(MenuBaseView, django_auth_views.LogoutView):
    template_name = 'fadderiet/utloggad.html'


class LoginCredentialsView(MenuBaseView, auth_views.LoginCred):
    template_name = 'fadderiet/logga-in/nollan.html'
    default_redirect_url = reverse_lazy('fadderiet:index')

    form_class = utils.make_crispy_form(auth_views.LoginCred.form_class, 'Logga in')

    extra_context = {
        'reset_password_url': reverse_lazy('fadderiet:aterstall-losenord:index'),
        'register_url': reverse_lazy('fadderiet:registrera-dig')
    }

class RegisterView(MenuBaseView, auth_views.AuthUserCreateView):
    template_name = 'fadderiet/registrera-dig.html'
    success_url = reverse_lazy('fadderiet:logga-in:index')

    form_class = utils.make_crispy_form(auth_views.AuthUserCreateView.form_class, 'Registrera')

class PasswordChangeView(auth_views.PasswordChangeView):
    success_url = reverse_lazy('authentication:password_change_done')
    template_name = 'authentication/password_change_form.html'

class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    template_name = 'authentication/password_change_done.html'

class PasswordResetView(MenuBaseView, auth_views.PasswordResetView):
    email_template_name = 'fadderiet/aterstall-losenord-epost.html'
    subject_template_name = 'fadderiet/aterstall-losenord-epost-amne.txt'
    success_url = reverse_lazy('fadderiet:aterstall-losenord:skickat')
    template_name = 'fadderiet/aterstall-losenord/index.html'
    form_class = utils.make_crispy_form(auth_views.PasswordResetView.form_class, submit_button='Återställ lösenord')

class PasswordResetDoneView(MenuBaseView, auth_views.PasswordResetDoneView):
    template_name = 'fadderiet/aterstall-losenord/skickat.html'

class PasswordResetConfirmView(MenuBaseView, auth_views.PasswordResetConfirmView):
    template_name = 'fadderiet/aterstall-losenord/lank.html'
    success_url = reverse_lazy('fadderiet:aterstall-losenord:klart')
    form_class = utils.make_crispy_form(auth_views.PasswordResetConfirmView.form_class, submit_button='Sätt nytt lösenord')

class PasswordResetCompleteView(MenuBaseView, auth_views.PasswordResetCompleteView):
    template_name = 'fadderiet/aterstall-losenord/klart.html'
    extra_context = {'login_url': reverse_lazy('fadderiet:logga-in:index')}


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    permission_denied_message = 'Denna sida är begränsad till inloggade användare.'
    template_name = 'fadderiet/mina-sidor/profil.html'
    model = apps.get_model(settings.USER_PROFILE_MODEL)
    fields = '__all__'

    def get_object(self, queryset=None):
        return self.request.user.profile

