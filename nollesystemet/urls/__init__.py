from django.conf import settings
from django.conf.urls import url
from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path
from django.conf.urls.static import static

import nollesystemet.views as views
import nollesystemet.admin as admin
from .fadderiet import fadderiet_urls
from .fohseriet import fohseriet_urls

urlpatterns = [
    path('fadderiet/', include(fadderiet_urls, namespace='fadderiet')),
    url(r'^fohseriet/admin/', admin.mottagningen_admin_site.urls, name='nolle-admin'),
    url(r'^fohseriet/super-admin/', admin.superadmin_admin_site.urls, name='super-admin'),
    path('fohseriet/', include(fohseriet_urls, namespace='fohseriet')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

