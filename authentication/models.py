from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group, AbstractBaseUser, PermissionsMixin
from .managers import AuthUserManager

class UserGroup(Group):
    """
    UserGroup
    Subclass of django.contrib.auth.models.Group defining groups of special permissions.

    Class attributes:
        is_external (django.db.models.BooleanField): Boolean telling if group is intended for use by authenticated
        users or not.
    """
    is_external = models.BooleanField()

class NolleGroup(Group):
    """
    Subclass of django.contrib.auth.models.Group defining groups of special permissions.
    Also contains extra information on the group itself.
    """
    description = models.TextField(max_length=1000, blank=True)
    logo = models.ImageField(null=True)

class AuthUser(AbstractBaseUser, PermissionsMixin):
    """
    Subclass of django.contrib.auth.models.AbstractBaseUser and django.contrib.auth.models.PermissionsMixin.
    User model for handling authentication and permissions. Makes it possible to authenticate either with
    username and password (auth_backend = 'CRED') or using external CAS authentication (auth_backend = 'CAS').

    Defines special group permissions to handle multiple group fields (user_group, nolle_group).
    """
    username = models.CharField(max_length=40, unique=True)
    USERNAME_FIELD = 'username'

    is_staff = models.BooleanField(
        'staff status',
        default=False,
        help_text='Designates whether the user can log into this admin site.',
    )
    AUTH_BACKEND_NAMES = ['CRED', 'CAS']
    auth_backend_choices = [*[(name, name) for name in AUTH_BACKEND_NAMES], ('__all__', 'All')]
    auth_backend = models.CharField(max_length=20, choices=auth_backend_choices)
    objects = AuthUserManager()

    group = None
    user_group = models.ForeignKey(UserGroup, null=True, on_delete=models.SET_NULL, default=None)
    nolle_group = models.ForeignKey(NolleGroup, null=True, on_delete=models.SET_NULL, default=None)

    # TODO: Add boolean for being done with profile setup. Do not authenticate without profile setup.

    def can_use_auth_method(self, backend_name):
        return self.auth_backend == '__all__' or self.auth_backend == backend_name

