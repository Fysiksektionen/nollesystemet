from django.urls import path
from django.contrib.auth.views import LoginView
from . import views

app_name = 'fohseriet'
urlpatterns = [
    path('', views.hello_world, name='index'),
    path('login/', LoginView.as_view(template_name="fohseriet/login.html"), name="login"),
    path('start/', views.hello_world, name='start'),
    path('hantera-evenemang/', views.hello_world, name='hantera_evenemang'),
    path('redigera-evenemang/<int:event_number>', views.hello_world, name='redigera_evenemang'),
    path('se-anmalan/<int:event_number>', views.hello_world, name='se_anmalan'),
    path('hantera-andvandare/', views.hello_world, name='hantera_andvandare'),
    path('redigera-andvandare/', views.hello_world, name='redigera_andvandare'),
]