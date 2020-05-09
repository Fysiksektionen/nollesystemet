from django.apps import apps
from django.conf import settings
from django.forms import ModelForm


class AuthUserUpdateForm(ModelForm):
    class Meta:
        model = apps.get_model(settings.AUTH_USER_MODEL)

class ProfileForm(ModelForm):
    class Meta:
        model = apps.get_model(settings.USER_PROFILE_MODEL)

