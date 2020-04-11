from django.urls import path

from . import views

app_name = 'fadderiet'
urlpatterns = [
    path('', views.hello_world, name='index'),
    path('schema/', views.hello_world, name='schema'),
    path('bra-info/', views.hello_world, name='bra_info'),
    path('om-fadderiet/', views.hello_world, name='om_fadderiet'),
    path('anmal-dig/', views.hello_world, name='anmal_dig'),
    path('kontakt/', views.hello_world, name='kontakt'),
    path('logga-in/', views.hello_world, name='logga_in'),
    path('mina-sidor/', views.hello_world, name='mina_sidor'),
    path('nolleenkaten/', views.hello_world, name='nolleenkaten'),
]