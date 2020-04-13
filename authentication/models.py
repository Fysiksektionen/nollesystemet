from django.db import models
from django.conf import settings
from django.forms import MultipleChoiceField
from django.contrib.auth.models import Group, AbstractBaseUser, PermissionsMixin
from .managers import AuthUserManager
from .model_fields import MultipleStringChoiceField

class UserGroup(Group):
    """
    Model for groups of special permissions.

    Class attributes:
        is_external: Boolean telling if group is intended for use by authenticated users or not.
    """
    is_external = models.BooleanField()

class NolleGroup(Group):
    """
    Model for "nØllegrupper". Can have special permissions.
    Also contains extra information on the group itself.
    """
    description = models.TextField(max_length=1000, blank=True)
    logo = models.ImageField(null=True)

class AuthUser(AbstractBaseUser, PermissionsMixin):
    """
    User model for handling authentication and permissions. Makes it possible to authenticate either with
    username and password (auth_backend = 'CRED') or using external CAS authentication (auth_backend = 'CAS').

    Defines special group permissions to handle multiple group fields (user_group, nolle_group).
    """
    # Username setup
    username = models.CharField(max_length=40, unique=True)
    USERNAME_FIELD = 'username'

    # Used only to give access to Admin panel
    is_staff = models.BooleanField(
        'staff status',
        default=False,
        help_text='Designates whether the user can log into this admin site.',
    )

    # Field for authorized authentication backends
    AUTH_BACKEND_NAMES = ['CRED', 'CAS']    # TODO: Dynamically link this to defined backends.
    auth_backend_choices = [*[(name, name) for name in AUTH_BACKEND_NAMES], ('__all__', 'All')]
    auth_backend = MultipleStringChoiceField(separator=",", choices=auth_backend_choices)

    objects = AuthUserManager()

    # Remove standard group and add two new groups
    group = None
    user_group = models.ManyToManyField(UserGroup, blank=True)
    nolle_group = models.ForeignKey(NolleGroup, blank=True, null=True, on_delete=models.SET_NULL)
    PERMISSION_GROUPS = ['user_group', 'nolle_group']   # Used by backend to determine what fields are group-references.

    has_set_profile = models.BooleanField(verbose_name="Profile setup done",
                                          default=False)

    def can_use_auth_method(self, backend_name):
        return '__all__' in self.auth_backend.split(",") or backend_name in self.auth_backend.split(",")

