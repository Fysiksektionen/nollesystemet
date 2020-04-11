from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group, AbstractBaseUser, PermissionsMixin
from .managers import AuthUserManager, UserProfileManager

class AuthUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=40, unique=True)
    kth_id = models.CharField(max_length=20, blank=True, unique=True)
    USERNAME_FIELD = 'username'

    is_staff = models.BooleanField(
        'staff status',
        default=False,
        help_text='Designates whether the user can log into this admin site.',
    )

    auth_backend_choices = [('DJANGO', 'Django'), ('CAS', 'CAS')]
    auth_backend = models.CharField(max_length=20, choices=auth_backend_choices)
    objects = AuthUserManager()


class UserGroup(Group):
    is_external = models.BooleanField()

class NolleGroup(Group):
    extra_info = models.TextField(max_length=1000, blank=True)

class UserProfile(models.Model):
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)

    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    food_preference = models.CharField(max_length=15, blank=True)
    contact_name = models.CharField(max_length=100, blank=True)
    contact_relation = models.CharField(max_length=100, blank=True)
    contact_phone_number = models.CharField(max_length=15, blank=True)

    user_group = models.ForeignKey(UserGroup, null=True, on_delete=models.SET_NULL, default=None)
    nolle_group = models.ForeignKey(NolleGroup, null=True, on_delete=models.SET_NULL, default=None)
    auth_user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")

    objects = UserProfileManager()

    def __str__(self):
        return str(self.first_name) + " " + str(self.last_name)
