from django.urls import include, path
from utils import helper_views
from .fadderiet import urlpatterns as fadderiet_urls
from .fohseriet import urlpatterns as fohseriet_urls

urlpatterns = [
    path('', helper_views.hello_world),
    path('fadderiet/', include(fadderiet_urls)),
    path('fohseriet/', include(fohseriet_urls)),
]