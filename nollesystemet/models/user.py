from django.db import models
import authentication.models as auth_models


class UserProfile(auth_models.UserProfile):
    kth_id = models.CharField(max_length=20, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    food_preference = models.CharField(max_length=150, blank=True)
    contact_name = models.CharField(max_length=100, blank=True)
    contact_relation = models.CharField(max_length=100, blank=True)
    contact_phone_number = models.CharField(max_length=15, blank=True)

    class Meta(auth_models.UserProfile.Meta):
        permissions = [
            ("edit_user_info", "Can edit user but not authentication stuff"),
            ("edit_user_registration", "Can change any user registration"),
        ]