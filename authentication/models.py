from annoying.fields import AutoOneToOneField
from django.conf import settings
from django.contrib.auth import get_backends
from django.contrib.auth.models import Group, AbstractBaseUser, PermissionsMixin, AbstractUser
from django.core import validators
from django.db import models

from .managers import AuthUserManager
from .model_fields import MultipleStringChoiceField

class AuthUser(AbstractUser):
    """
    User model for handling authentication and permissions. Makes it possible to authenticate either with
    username and password (auth_backend = 'CRED') or using external CAS authentication (auth_backend = 'CAS').
    """

    # Remove unwanted inherited things
    first_name = None
    last_name = None
    date_joined = None

    # Field for authorized authentication backends
    auth_backend = MultipleStringChoiceField(separator=",", choices=None, max_length=150)
    objects = AuthUserManager()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        auth_backend_names = [backend.backend_name for backend in get_backends()
                              if hasattr(backend, 'backend_name')]
        self._meta.get_field('auth_backend').choices = [*[(name, name) for name in auth_backend_names],
                                                        ('__all__', 'All')]

    def can_use_auth_method(self, backend_name):
        return '__all__' in self.auth_backend.split(",") or backend_name in self.auth_backend.split(",")

    def clean(self):
        super().clean()
        kth_id_validator = validators.RegexValidator(regex="^u1.*$", message="You can not start a username with 'u1'.", inverse_match=True)
        kth_id_validator(getattr(self, self.USERNAME_FIELD))

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class UserProfile(models.Model):
    """
    User profile model base class. Defines the basic behaviour of a user profile and contains a one-to-one field to an
    AUTH_USER_MODEL.

    Since this model is automatically instantiated at AUTH_USER_MODEL creation all fields must be blankable
    or have a default.
    """

    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)

    auth_user = AutoOneToOneField(settings.AUTH_USER_MODEL,
                                  on_delete=models.CASCADE,
                                  related_name="profile",
                                  null=False,
                                  unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        if str(self.first_name):
            return '%s %s' % (str(self.first_name), str(self.last_name))
        else:
            return str(getattr(self.auth_user, self.auth_user.USERNAME_FIELD))

    @property
    def name(self):
        try:
            return '%s %s' % (str(self.first_name), str(self.last_name))
        except:
            return 'User have no name set'

    @property
    def email(self):
        try:
            return '%s' % str(self.auth_user.email)
        except:
            return 'User profile has no AuthUser'
