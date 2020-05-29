from django.apps import apps
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, UpdateView

import authentication.utils as utils
from authentication.forms import UserCreationForm
from authentication.views.login import _login_success_redirect


class AuthUserCreateView(FormView):
    template_name = 'authentication/authuser_create.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('authentication:login')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

class AuthUserUpdateView(UpdateView, LoginRequiredMixin, UserPassesTestMixin):
    """
    AuthUser edit view. Does not allow password change. This can be done separately.
    Redirects to login if not authenticated or with permission.
    """

    model = apps.get_model(utils2.get_setting('AUTH_USER_MODEL'))
    fields = ['username', 'email']
    template_name_suffix = '_update_form'

    success_url = reverse_lazy('authentication:index')

    def get_success_url(self):
        if REDIRECT_FIELD_NAME in self.request.GET:
            return self.request.GET[REDIRECT_FIELD_NAME]
        else:
            return self.success_url

    def test_func(self):
        return str(self.request.user.pk) == self.kwargs['pk']

    def get_login_url(self):
        if not self.request.user.is_authenticated:
            return utils2.get_setting('LOGIN_URL') + '?' + REDIRECT_FIELD_NAME + "=" + \
                   reverse('authentication:update_auth_user', kwargs={'pk': self.kwargs['pk']})
        else:
            return _login_success_redirect(self.request,
                                           self.request.user,
                                           self.success_url)

class UserProfileUpdateView(UpdateView, LoginRequiredMixin, UserPassesTestMixin):
    """
    UserProfile edit view.
    Redirects to login if not authenticated or with permission.
    """

    model = apps.get_model(utils2.get_setting('USER_PROFILE_MODEL'))
    fields = [field.name for field in model._meta.get_fields() if field.name not in ['has_set_profile', 'auth_user']]
    template_name_suffix = '_update_form'

    success_url = reverse_lazy('authentication:index')

    def get_success_url(self):
        if REDIRECT_FIELD_NAME in self.request.GET:
            return self.request.GET[REDIRECT_FIELD_NAME]
        else:
            return self.success_url

    def test_func(self):
        return str(self.request.user.pk) == self.kwargs['pk']

    def get_login_url(self):
        if not self.request.user.is_authenticated:
            return utils2.get_setting('LOGIN_URL') + '?' + REDIRECT_FIELD_NAME + "=" + \
                   reverse('authentication:update_auth_user', kwargs={'pk': self.kwargs['pk']})
        else:
            return _login_success_redirect(self.request,
                                           self.request.user,
                                           self.success_url)

    def form_valid(self, form):
        form.instance.has_set_profile = True
        return super().form_valid(form)

