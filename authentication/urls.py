from django.urls import path
from django.shortcuts import reverse, resolve_url
from .views import Login, LoginCred, LoginCas
from django.views.generic.base import TemplateView

# TODO: Define paths for all authentication and user functions.
# TODO: User relative (dynamic) paths in redirect urls.
app_name = 'authentication'
urlpatterns = [
    path('login/', Login.as_view(cas_login_url='/auth/login/cas/',
                                 cred_login_url='/auth/login/cred/',
                                 default_redirect_url='/auth/get_post_vars/'), name="login"),
    path('login/cred/', LoginCred.as_view(default_redirect_url='/auth/get_post_vars/'), name="login_cred"),
    path('login/cas/', LoginCas.as_view(default_redirect_url='/auth/get_post_vars/'), name="login_cas"),
    path('get_post_vars/', TemplateView.as_view(template_name='authentication/print_get_post.html'), name="get_post_vars"),
]