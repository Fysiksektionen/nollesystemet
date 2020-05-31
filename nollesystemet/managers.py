from django.contrib.auth.models import BaseUserManager
from django.apps import apps
from django.conf import settings


class UserProfileManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, first_name, last_name, password, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')
        username = apps.get_model(settings.AUTH_USER_MODEL).normalize_username(username)

        is_staff = extra_fields.pop('is_staff')
        is_superuser = extra_fields.pop('is_superuser')

        auth_user = apps.get_model(settings.AUTH_USER_MODEL)(username=username,
                                                             is_staff=is_staff,
                                                             is_superuser=is_superuser)
        auth_user.set_password(password)
        auth_user.save(using=self._db)

        user_profile = self.model(first_name=first_name, last_name=last_name, auth_user=auth_user, **extra_fields)

        user_profile.save()

        return user_profile

    def create_user(self, username, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, first_name, last_name, password, **extra_fields)

    def create_superuser(self, username, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(username, first_name, last_name, password, **extra_fields)