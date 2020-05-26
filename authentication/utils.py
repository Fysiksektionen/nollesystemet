from urllib.parse import urlunparse, urlencode

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import resolve_url

# TODO: Understand and modify functions. Remove any unwanted or unnecessary functionality.

DEFAULT_SETTING_VALUES = {
    'CAS_SERVER_URL': 'https://login.kth.se/',
}

def get_setting(setting_name):
    """
    Returns the value of the setting with the provided name
    if set. Returns the value in DEFAULT_SETTING_VALUES
    otherwise.
    """
    try:
        return getattr(settings, setting_name)
    except AttributeError:
        try:
            return DEFAULT_SETTING_VALUES[setting_name]
        except KeyError:
            return None


def get_redirect_url(request, use_referer=False, default_url=None):
    """
    Returns the URL to redirect to once business at the current
    URL is completed.

    Picks the first usable URL from the following list:
      1. URL provided as GET parameter under REDIRECT_FIELD_NAME
      2. Referring page if use_referer is True, and set in header
      3. default_url parameter
    """
    redirect_url = request.GET.get(REDIRECT_FIELD_NAME)
    if not redirect_url:
        if use_referer:
            redirect_url = request.META.get('HTTP_REFERER')
        if not redirect_url:
            redirect_url = resolve_url(default_url)
        prefix = urlunparse(
                ('https' if request.is_secure() else 'http', request.get_host(), '', '', '', ''),
        )
        if redirect_url.startswith(prefix):
            redirect_url = redirect_url[len(prefix):]
    return redirect_url


def get_service_url(request, redirect_url=None):
    """
    Returns the service URL to provide to the CAS
    server for the provided request.

    Accepts an optional redirect_url, which defaults
    to the value of get_redirect_url(request).
    """
    service_url = urlunparse(
            ('https' if request.is_secure() else 'http', request.get_host(),
            request.path, '', '', ''),
    )
    query_params = request.GET.copy()
    query_params[REDIRECT_FIELD_NAME] = redirect_url or get_redirect_url(request)
    # The CAS server may have added the ticket as an extra query
    # parameter upon checking the credentials - ensure it is ignored
    query_params.pop('ticket', None)
    service_url += '?' + urlencode(query_params)
    return service_url