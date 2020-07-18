from django.urls import include, path

import authentication.views as auth_views
import nollesystemet.views as views

login_urls = ([
    path('', views.LoginViewFadderiet.as_view(), name='index'),
    path('nollan/', views.LoginCredentialsViewFadderiet.as_view(), name='nollan'),
    path('fadder/', views.custom_redirect_view, kwargs={'redirect_name': 'fadderiet:logga-in:cas'},
         name='fadder'),
    path('cas/', auth_views.login.LoginCas.as_view(), name='cas'),
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

happening_urls = ([
    path('', views.HappeningListViewFadderiet.as_view(), name='index'),
    path('<int:pk>/anmalan', views.RegistrationView.as_view(), name='anmalan'),
], 'evenemang')


fadderiet_urls = ([
    path('', views.misc.FadderietMenuView.as_view(
        template_name='fadderiet/index.html',
        site_name="Fadderiet: index",
        site_texts=['title', 'valkommen_text'],
        site_images=['banner']),
         name='index'),
    path('schema/', views.FadderietMenuView.as_view(
        template_name='fadderiet/schema.html',
        site_name="Fadderiet: schema",
        site_texts=['intro'],
        site_images=['schema']),
         name='schema'),
    path('bra-info/', views.FadderietMenuView.as_view(
        template_name="fadderiet/bra-info.html",
        site_name="Fadderiet: Bra info",
        site_texts=['body']),
         name='bra-info'),
    path('om-fadderiet/', views.FadderietMenuView.as_view(
        template_name="fadderiet/om-fadderiet.html",
        site_name="Fadderiet: Om fadderiet",
        site_texts=['body']
    ), name='om-fadderiet'),
    path('kontakt/', views.FadderietMenuView.as_view(
        template_name="fadderiet/kontakt.html",
        site_name="Fadderiet: Kontakt",
        site_texts=['body']
    ), name='kontakt'),
    path('saknar-rattigheter/', views.misc.AccessDeniedViewFadderiet.as_view(), name='saknar-rattigheter'),

    path('nolleenkaten/', views.NolleFormView.as_view(), name='nolleenkaten'),

    path('evenemang/', include(happening_urls)),
    path('logga-in/', include(login_urls)),
    path('logga-ut/', views.authentication.LogoutViewFadderiet.as_view(), name='logga-ut'),
    path('aterstall-losenord/', include(password_reset_urls)),
    path('byt-losenord/', include(password_change_urls)),
    path('mina-sidor/', include(my_pages_urls)),

], 'fadderiet')

