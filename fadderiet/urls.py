import django.contrib.auth.views as django_auth_views
from django.urls import include, path

import authentication.views as auth_views
from . import views

app_name = 'fadderiet'

login_urls = ([
    path('', views.LoginView.as_view(), name='index'),
    path('nollan/', views.LoginCredentialsView.as_view(), name='nollan'),
    path('fadder/', views.custom_redirect_view, kwargs={'redirect_name': 'fadderiet:logga-in:cas'},
         name='fadder'),
    path('cas/', auth_views.LoginCas.as_view(), name='cas'),
], 'logga-in')

password_reset_urls = ([
    path('', views.hello_world, name='index'),
    path('skickat/', views.hello_world, name='skickat'),
    path('<uidb64>/<token>/', views.hello_world, name='lank'),
    path('klart/', views.hello_world, name='klart'),
], 'aterstall-losenord')

my_pages_urls = ([
    path('profil/', views.hello_world, name='profil'),
], 'mina-sidor')

urlpatterns = [
    path('', views.MenuBaseView.as_view(template_name='fadderiet/index.html'),
         name='index'),
    path('schema/', views.hello_world, name='schema'),
    path('bra-info/', views.hello_world, name='bra-info'),
    path('om-fadderiet/', views.hello_world, name='om-fadderiet'),
    path('anmal-dig/', views.hello_world, name='anmal-dig'),
    path('kontakt/', views.hello_world, name='kontakt'),
    path('mina-sidor/', views.hello_world, name='mina-sidor'),
    path('nolleenkaten/', views.hello_world, name='nolleenkaten'),

    path('logga-in/', include(login_urls)),
    path('logga-ut/', django_auth_views.LoginView.as_view(template_name="fadderiet/utloggad.html"), name='logga-ut'),
    path('registrera-dig/', views.RegisterView.as_view(), name='registrera-dig'),
    path('aterstall-losenord/', include(password_reset_urls)),
    path('byt-losenord/', views.hello_world, name='byt-losenord'),
    path('mina-sidor/', include(my_pages_urls)),
]