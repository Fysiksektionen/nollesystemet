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
    User model for handling authentication and permissions.
    """

    # Remove unwanted inherited things
    first_name = None
    last_name = None
    date_joined = None

    # Field for authorized authentication backends
    objects = AuthUserManager()

    def clean(self):
        super().clean()
        kth_id_validator = validators.RegexValidator(regex="^u1.*$", message="You can not start a username with 'u1'.", inverse_match=True)
        kth_id_validator(getattr(self, self.USERNAME_FIELD))

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def can_set_password(self):
        return self.has_usable_password()


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
                                  null=True,
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
