from django.urls import path, reverse_lazy
from django.contrib.auth.views import LoginView
from . import views
from .views import *

app_name = 'fohseriet'
urlpatterns = [
    path('', views.index, name='index'),
    path('login/', LoginView.as_view(template_name="fohseriet/login.html"), name="login"),
    path('evenemang', HappeningListView.as_view(), name="happening-list"),
    path('evenemang/<int:pk>/', HappeningUpdateView.as_view(), name='happening-update'),
    path('skapa-evenemang', HappeningCreateView.as_view(), name='create_happening'),
]