from django.contrib.auth import get_backends
from django.contrib.auth.models import Group, AbstractBaseUser, PermissionsMixin, AbstractUser
from django.db import models

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


class AuthUser(AbstractUser):
    """
    User model for handling authentication and permissions. Makes it possible to authenticate either with
    username and password (auth_backend = 'CRED') or using external CAS authentication (auth_backend = 'CAS').
    """

    # Remove unwanted inherited things
    group = None
    first_name = None
    last_name = None
    date_joined = None

    # Field for authorized authentication backends
    auth_backend = MultipleStringChoiceField(separator=",", choices=None, max_length=150)

    # Remove standard group and add two new groups
    user_group = models.ManyToManyField(UserGroup, blank=True)
    nolle_group = models.ForeignKey(NolleGroup, blank=True, null=True, on_delete=models.SET_NULL)
    PERMISSION_GROUPS = ['user_group', 'nolle_group']  # Used by backend to determine what fields are group-references.

    has_set_profile = models.BooleanField(verbose_name="Profile setup done",
                                          default=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        auth_backend_names = [backend.backend_name for backend in get_backends()
                              if hasattr(backend, 'backend_name')]
        self._meta.get_field('auth_backend').choices = [*[(name, name) for name in auth_backend_names],
                                                        ('__all__', 'All')]

    def can_use_auth_method(self, backend_name):
        return '__all__' in self.auth_backend.split(",") or backend_name in self.auth_backend.split(",")
