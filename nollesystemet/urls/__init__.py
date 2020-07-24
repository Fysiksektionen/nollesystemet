from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static

import nollesystemet.views as views
from .fadderiet import fadderiet_urls
from .fohseriet import fohseriet_urls

urlpatterns = [
    path('', views.custom_redirect_view, kwargs={'redirect_name': 'fadderiet:index'}),
    path('fadderiet/', include(fadderiet_urls, namespace='fadderiet')),
    path('fohseriet/', include(fohseriet_urls, namespace='fohseriet')),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

