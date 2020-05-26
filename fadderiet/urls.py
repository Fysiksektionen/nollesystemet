from django.urls import include, path

import authentication.views as auth_views
from utils import helper_views
from . import views

app_name = 'fadderiet'

login_urls = ([
    path('', views.LoginView.as_view(), name='index'),
    path('nollan/', views.LoginCredentialsView.as_view(), name='nollan'),
    path('fadder/', helper_views.custom_redirect_view, kwargs={'redirect_name': 'fadderiet:logga-in:cas'},
         name='fadder'),
    path('cas/', auth_views.LoginCas.as_view(), name='cas'),
], 'logga-in')

password_reset_urls = ([
    path('', views.PasswordResetView.as_view(), name='index'),
    path('skickat/', views.PasswordResetDoneView.as_view(), name='skickat'),
    path('<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='lank'),
    path('klart/', views.PasswordResetCompleteView.as_view(), name='klart'),
], 'aterstall-losenord')

password_change_urls = ([
    path('', views.PasswordChangeView.as_view(), name='index'),
    path('klart/', views.PasswordChangeDoneView.as_view(), name='klart'),
], 'byt-losenord')

my_pages_urls = ([
    path('profil/', views.ProfilePageView.as_view(), name='profil'),
], 'mina-sidor')

urlpatterns = [
    path('', views.MenuView.as_view(template_name='fadderiet/index.html'),
         name='index'),
    path('schema/', helper_views.hello_world, name='schema'),
    path('bra-info/', helper_views.hello_world, name='bra-info'),
    path('om-fadderiet/', helper_views.hello_world, name='om-fadderiet'),
    path('anmal-dig/', helper_views.hello_world, name='anmal-dig'),
    path('kontakt/', helper_views.hello_world, name='kontakt'),
    path('mina-sidor/', helper_views.hello_world, name='mina-sidor'),
    path('nolleenkaten/', helper_views.hello_world, name='nolleenkaten'),

    path('logga-in/', include(login_urls)),
    path('logga-ut/', views.LogoutView.as_view(), name='logga-ut'),
    path('registrera-dig/', views.RegisterView.as_view(), name='registrera-dig'),
    path('aterstall-losenord/', include(password_reset_urls)),
    path('byt-losenord/', include(password_change_urls)),
    path('mina-sidor/', include(my_pages_urls)),
]