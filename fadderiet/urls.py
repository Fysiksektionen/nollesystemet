from django.urls import include, path

import fadderiet.utils as utils
from . import views

app_name = 'fadderiet'

login_urls = ([
    path('', views.LoginView.as_view(), name='index'),
    path('nollan/', views.LoginCredentialsView.as_view(), name='nollan'),
    path('fadder/', views.custom_redirect_view, kwargs={'redirect_name': 'fadderiet:logga-in:cas'},
         name='fadder'),
    path('cas/', views.hello_world, name='cas'),
], app_name)

password_reset_urls = ([
    path('', views.hello_world, name='index'),
    path('skickat/', views.hello_world, name='skickat'),
    path('<uidb64>/<token>/', views.hello_world, name='lank'),
    path('klart/', views.hello_world, name='klart'),
], app_name)

my_pages_urls = ([
    path('profil/', views.hello_world, name='profil'),
], app_name)

urlpatterns = [
    path('', views.MenuBaseView.as_view(template_name='fadderiet/index.html',
                                        menu_item_info=utils.menu_item_info,
                                        menu_items=['index', 'schema', 'bra-info', 'anmal-dig', 'kontakt', ['mina-sidor', 'logga-in']]),
         name='index'),
    path('schema/', views.hello_world, name='schema'),
    path('bra-info/', views.hello_world, name='bra-info'),
    path('om-fadderiet/', views.hello_world, name='om-fadderiet'),
    path('anmal-dig/', views.hello_world, name='anmal-dig'),
    path('kontakt/', views.hello_world, name='kontakt'),
    path('mina-sidor/', views.hello_world, name='mina-sidor'),
    path('nolleenkaten/', views.hello_world, name='nolleenkaten'),

    path('logga-in/', include(login_urls, namespace='logga-in')),
    path('registrera-dig/', views.hello_world, name='registrera-dig'),
    path('aterstall-losenord/', include(password_reset_urls, namespace='aterstall-losenord')),
    path('byt-losenord/', views.hello_world, name='byt-losenord'),
    path('mina-sidor/', include(my_pages_urls, namespace='mina-sidor')),
]