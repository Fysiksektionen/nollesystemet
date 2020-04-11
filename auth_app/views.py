from django.shortcuts import render
from django.contrib.auth.views import LoginView as DjangoAuthLoginView

class LoginView(DjangoAuthLoginView):
    pass
