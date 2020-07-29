from django.contrib.auth.models import BaseUserManager
from django.apps import apps
from django.conf import settings

class UserProfileManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, password, first_name, last_name, user_type, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')
        username = apps.get_model(settings.AUTH_USER_MODEL).normalize_username(username)

        auth_user = apps.get_model(
            settings.AUTH_USER_MODEL
        ).objects.create_user(username=username,
                              password=password,
                              is_staff=extra_fields.pop('is_staff', False),
                              is_superuser=extra_fields.pop('is_superuser', False),
                              email=extra_fields.pop('email', None),
                              )

        user_profile = self.model(first_name=first_name,
                                  last_name=last_name,
                                  auth_user=auth_user,
                                  user_type=user_type,
                                  **extra_fields)
        user_profile.save()

        return user_profile

    def create_user(self, username, password, first_name, last_name, user_type, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, first_name, last_name, user_type, **extra_fields)

    def create_superuser(self, username, password, first_name, last_name, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, password, first_name, last_name, self.model.UserType.ADMIN, **extra_fields)
