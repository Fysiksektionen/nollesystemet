from django.contrib.auth.views import LogoutView
from django.urls import path
from django.views.generic.base import TemplateView

from .views import *

# TODO: Define paths for all authentication and user functions.
# TODO: User relative (dynamic) paths in redirect urls.
app_name = 'authentication'
urlpatterns = [
    path('login/', Login.as_view(), name="login"),
    path('login/cred/', LoginCred.as_view(), name="login_cred"),
    path('login/cas/', LoginCas.as_view(), name="login_cas"),
    
    path('logout/', LogoutView.as_view(next_page='authentication:request_info'), name="logout"),
    
    path('signup/', Login.as_view(), name="login"),
    path('signup/cred/', Login.as_view(), name="login"),
    path('signup/cas', Login.as_view(), name="login"),
    
    path('password/reset/', Login.as_view(), name="login"),
    path('password/change/', Login.as_view(), name="login"),

    path('cas_fake/', FakeCASLogin.as_view(), name='fake_cas'),
    path('cas_fake/login/', FakeCASLogin.as_view(), name='fake_cas_login'),
    path('cas_fake/logout/', FakeCASLogout.as_view(), name='fake_cas_logout'),

    path('request_info/', TemplateView.as_view(template_name='authentication/print_get_post.html'), name='request_info')
]