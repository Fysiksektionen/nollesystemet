from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group, AbstractBaseUser, PermissionsMixin
from .managers import AuthUserManager

class UserGroup(Group):
    is_external = models.BooleanField()

class NolleGroup(Group):
    description = models.TextField(max_length=1000, blank=True)
    logo = models.ImageField(null=True, blank=True)

class AuthUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=40, unique=True)
    USERNAME_FIELD = 'username'

    is_staff = models.BooleanField(
        'staff status',
        default=False,
        help_text='Designates whether the user can log into this admin site.',
    )

    auth_backend_choices = [('CRED', 'Credentials'), ('CAS', 'CAS')]
    auth_backend = models.CharField(max_length=20, choices=auth_backend_choices)
    objects = AuthUserManager()

    user_group = models.ForeignKey(UserGroup, null=True, on_delete=models.SET_NULL, default=None)
    nolle_group = models.ForeignKey(NolleGroup, null=True, on_delete=models.SET_NULL, default=None)
