from django.urls import include, path
import nollesystemet.views as views
from .fadderiet import fadderiet_urls
from .fohseriet import fohseriet_urls

urlpatterns = [
    path('', views.hello_world),
    path('fadderiet/', include(fadderiet_urls)),
    path('fohseriet/', include(fohseriet_urls)),
]