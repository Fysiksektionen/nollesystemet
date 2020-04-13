from urllib.parse import urlencode

import cas
from django.contrib.auth import REDIRECT_FIELD_NAME, authenticate, login as django_login, logout as django_logout
from django.contrib.auth.views import LoginView
from django.forms import Form
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView

import authentication.utils as utils
from .forms import CredAuthenticationForm, FakeCASLoginForm


def _login_success_redirect(request, user, next_url, drop_params=None):
    """
    Determines where to go upon successful authentication:
    Redirects to link tmp account page if user is a temporary
    user, redirects to next_url otherwise.

    Any query parameters whose key exists in drop_params are
    not propogated to the destination URL
    """
    query_params = request.GET.copy()
    print(query_params, drop_params)
    # Drop all blacklisted query parameters
    if drop_params:
        for key in drop_params:
            if key in query_params:
                del query_params[key]

    print(query_params, drop_params)

    # TODO: Write redirect for user that has not yet filed their profile.

    suffix = ''
    if REDIRECT_FIELD_NAME in query_params:
        del query_params[REDIRECT_FIELD_NAME]
    if len(query_params) > 0:
        suffix = '?' + query_params.urlencode()
    return HttpResponseRedirect(next_url + suffix)

class Login(TemplateView):
    # TODO: Write docstring.

    template_name = 'authentication/login.html'
    cred_login_url = reverse_lazy('authentication:login_cred')
    cas_login_url = reverse_lazy('authentication:login_cas')
    default_redirect_url = reverse_lazy('authentication:request_info')

    def get(self, request, *args, **kwargs):
        # TODO: Understand and fix GET-param logic.
        # Determine redirect url
        next_url = utils.get_redirect_url(request, default_url=self.default_redirect_url)

        # If the user is already authenticated, proceed to next page
        if request.user.is_authenticated:
            return _login_success_redirect(request, request.user, next_url)

        params = request.GET.copy()
        params.setdefault(REDIRECT_FIELD_NAME, next_url)
        get_params = params.urlencode()
        kwargs.update({
            'cred_login_url': self.cred_login_url + ('?' + get_params if get_params else ''),
            'cas_login_url': self.cas_login_url + ('?' + get_params if get_params else '')
        })

        return super().get(request, *args, **kwargs)


class LoginCred(LoginView):
    # TODO: Write docstring.

    form_class = CredAuthenticationForm
    template_name = 'authentication/login_cred.html'
    default_redirect_url = reverse_lazy('authentication:request_info')

    def get_redirect_url(self):
        return super().get_redirect_url() or self.default_redirect_url

    def form_valid(self, form):
        return super().form_valid(form)


class LoginCas(View):
    """
    Redirects to the CAS login URL, or verifies the
    CAS ticket, if provided.
    """
    default_redirect_url = reverse_lazy('authentication:request_info')

    def get(self, request):

        ticket = request.GET.get('ticket')
        next_url = request.GET.get(REDIRECT_FIELD_NAME)

        if not next_url:
            next_url = utils.get_redirect_url(request, default_url=self.default_redirect_url, use_referer=True)

        # If the user is already authenticated, proceed to next page
        if request.user.is_authenticated:
            return _login_success_redirect(request, request.user, next_url)

        service_url = utils.get_service_url(request, next_url)
        # TODO: Check if this holds for fake CAS server.
        client = cas.CASClient(version=2, service_url=service_url, server_url=str(utils.get_setting('CAS_SERVER_URL')))

        # If a ticket was provided, attempt to authenticate with it
        if ticket:
            user = authenticate(request=request, ticket=ticket, service=service_url)

            # Authentication successful: setup session + proceed
            if user:
                if not request.session.exists(request.session.session_key):
                    request.session.create()
                django_login(request, user)
                return _login_success_redirect(request, user, next_url, ["ticket", "service"])

            # Authentication failed: raise permission denied
            else:
                raise Exception("Verification of CAS ticket failed.")

        # If no ticket was provided, redirect to the
        # login URL for the institution's CAS server
        else:
            return HttpResponseRedirect(client.get_login_url())

class FakeCASLogin(FormView):
    template_name = 'authentication/login_cas_fake.html'
    form_class = FakeCASLoginForm

    def form_valid(self, form):
        url = self.request.GET['service']
        url += '&' + urlencode({'ticket': form.cleaned_data['username']})
        return HttpResponseRedirect(url)


class FakeCASLogout(FormView):
    template_name = 'authentication/logout_cas_fake.html'
    form_class = Form

    def form_valid(self, form):
        django_logout(request=self.request)
        if REDIRECT_FIELD_NAME in self.request.GET:
            return HttpResponseRedirect(self.request.GET[REDIRECT_FIELD_NAME])
        return HttpResponseRedirect(reverse('authentication:request_info'))


# TODO: Write views for all authentication and user functionality.
