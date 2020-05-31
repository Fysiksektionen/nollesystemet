from django.urls import include, path

import authentication.views as auth_views
import nollesystemet.views as views

login_urls = ([
    path('', views.authentication.LoginViewFadderiet.as_view(), name='index'),
    path('nollan/', views.authentication.LoginCredentialsViewFadderiet.as_view(), name='nollan'),
    path('fadder/', views.custom_redirect_view, kwargs={'redirect_name': 'fadderiet:logga-in:cas'},
         name='fadder'),
    path('cas/', auth_views.login.LoginCas.as_view(), name='cas'),
], 'logga-in')

password_reset_urls = ([
    path('', views.authentication.PasswordResetView.as_view(), name='index'),
    path('skickat/', views.authentication.PasswordResetDoneView.as_view(), name='skickat'),
    path('<uidb64>/<token>/', views.authentication.PasswordResetConfirmView.as_view(), name='lank'),
    path('klart/', views.authentication.PasswordResetCompleteView.as_view(), name='klart'),
], 'aterstall-losenord')

password_change_urls = ([
    path('', views.authentication.PasswordChangeView.as_view(), name='index'),
    path('klart/', views.authentication.PasswordChangeDoneView.as_view(), name='klart'),
], 'byt-losenord')

my_pages_urls = ([
    path('profil/', views.user.ProfilePageView.as_view(), name='profil'),
], 'mina-sidor')

happening_urls = ([
    path('', views.happening.HappeningListViewFadderiet.as_view(), name='index'),
    path('<int:pk>/anmalan', views.registration.RegistrationView.as_view(), name='anmalan'),
], 'evenemang')

fadderiet_urls = ([
    path('', views.misc.FadderietMenuView.as_view(template_name='fadderiet/index.html'),
         name='index'),
    path('schema/', views.hello_world, name='schema'),
    path('bra-info/', views.hello_world, name='bra-info'),
    path('om-fadderiet/', views.hello_world, name='om-fadderiet'),
    path('kontakt/', views.hello_world, name='kontakt'),
    path('mina-sidor/', views.hello_world, name='mina-sidor'),
    path('nolleenkaten/', views.hello_world, name='nolleenkaten'),

    path('evenemang/', include(happening_urls)),
    path('logga-in/', include(login_urls)),
    path('logga-ut/', views.authentication.LogoutView.as_view(), name='logga-ut'),
    path('registrera-dig/', views.authentication.RegisterView.as_view(), name='registrera-dig'),
    path('aterstall-losenord/', include(password_reset_urls)),
    path('byt-losenord/', include(password_change_urls)),
    path('mina-sidor/', include(my_pages_urls)),
], 'fadderiet')

