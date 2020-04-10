from django.contrib import admin
from uniauth import models
from .utils import get_user_profile_model

admin.site.register(get_user_profile_model())
admin.site.register(models.LinkedEmail)
admin.site.register(models.Institution)
admin.site.register(models.InstitutionAccount)
