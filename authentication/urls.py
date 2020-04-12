from django.urls import path
from .views import Login

app_name = 'authentication'
urlpatterns = [
    path('login/', Login.as_view(template_name="authentication/login.html",
                                     cred_login_url='/',
                                     cas_login_url='/'
                                     ), name="login"),
]