from django.apps import apps
from django.contrib.auth.models import BaseUserManager

import authentication.utils as utils


class AuthUserManager(BaseUserManager):
    """
    Manager that defines special behaviors and good-to-have functions on models.
    Defines functions for user creation with automatic creation of linking USER_PROFILE_MODEL.
    """

    use_in_migrations = True

    def _create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')
        username = self.model.normalize_username(username)

        extra_fields.setdefault('email', username + "@f.kth.se")

        user = self.model(username=username, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()




        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, password, **extra_fields)
