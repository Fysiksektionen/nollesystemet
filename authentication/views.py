from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic.base import TemplateView
from django.contrib.auth import REDIRECT_FIELD_NAME

def _login_success_redirect(request, user, next_url):
    # TODO: Write redirect for user that has not yet filed their profile.

    suffix = ''
    if REDIRECT_FIELD_NAME in request.GET:
        del request.GET[REDIRECT_FIELD_NAME]
    if len(request.GET) > 0:
        suffix = '?' + request.GET.urlencode()
    return HttpResponseRedirect(next_url + suffix)

class Login(TemplateView):
    template_name = None
    cred_login_url = None
    cas_login_url = None
    default_redirect_url = None
    redirect_field_name = REDIRECT_FIELD_NAME

    def get(self, request, *args, **kwargs):
        # Determine redirect url
        next_url = request.GET.get(REDIRECT_FIELD_NAME)
        if not next_url:
            next_url = self.default_redirect_url

        # If the user is already authenticated, proceed to next page
        if request.user.is_authenticated:
            return _login_success_redirect(request, request.user, next_url)

        params = request.GET
        params.appendlist(REDIRECT_FIELD_NAME, next_url)
        get_params = params.encode()
        kwargs.update({
            'cred_login_url': self.cred_login_url + ('?' + get_params if get_params else ''),
            'cas_login_url': self.cas_login_url + ('?' + get_params if get_params else '')
        })

        return super().get(request, *args, **kwargs)
