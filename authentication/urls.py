from django.urls import path
from django.urls import reverse, reverse_lazy
from .views import Login, LoginCred, LoginCas
from django.views.generic.base import TemplateView

# TODO: Define paths for all authentication and user functions.
# TODO: User relative (dynamic) paths in redirect urls.
app_name = 'authentication'
urlpatterns = [
    path('login/', Login.as_view(), name="login"),
    path('login/cred/', LoginCred.as_view(), name="login_cred"),
    path('login/cas/', LoginCas.as_view(), name="login_cas"),
    
    path('logout/', Login.as_view(), name="logout"),
    
    path('signup/', Login.as_view(), name="login"),
    path('signup/cred/', Login.as_view(), name="login"),
    path('signup/cas', Login.as_view(), name="login"),
    
    path('password/reset/', Login.as_view(), name="login"),
    path('password/change/', Login.as_view(), name="login"),
]