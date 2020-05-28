from django.conf import settings
from django.db import models
from django.db.models import Q

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
            ("edit_user_registrations", "Can change a users registration"),
        ]


class Happening(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=300)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    image_file_path = models.CharField(max_length=50)

    takes_registration = models.BooleanField()
    external_registration = models.BooleanField()
    user_groups = models.ManyToManyField(auth_models.UserGroup, related_name="happening_user_group")
    nolle_groups = models.ManyToManyField(auth_models.NolleGroup, related_name="happening_nolle_group")

    food = models.BooleanField(default=True)

    editors = models.ManyToManyField(settings.USER_PROFILE_MODEL,
                                     limit_choices_to=((
                                             Q(auth_user__user_group__permissions__codename='edit_happening') |
                                             Q(auth_user__user_permissions__codename='edit_happening')
                                     )))

    class Meta(auth_models.UserProfile.Meta):
        permissions = [
            ("edit_happening", "Can edit/create happenings"),
        ]

    def __str__(self):
        return str(self.name)


class GroupBasePrice(models.Model):
    group = models.ForeignKey(auth_models.UserGroup, on_delete=models.CASCADE)
    happening = models.ForeignKey(Happening, on_delete=models.CASCADE)
    base_price = models.IntegerField()

    def __str__(self):
        return str(self.group) + " (" + str(self.base_price) + "kr)"


class DrinkOption(models.Model):
    happening = models.ForeignKey(Happening, on_delete=models.CASCADE)
    drink = models.CharField(max_length=30)
    price = models.IntegerField()

    def __str__(self):
        return str(self.drink) + " (" + str(self.price) + "kr)"


class ExtraOption(models.Model):
    happening = models.ForeignKey(Happening, on_delete=models.CASCADE)
    extra_option = models.CharField(max_length=30)
    price = models.IntegerField()

    def __str__(self):
        return str(self.extra_option) + " (" + str(self.price) + "kr)"


class Registration(models.Model):
    happening = models.ForeignKey(Happening, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.USER_PROFILE_MODEL, on_delete=models.CASCADE)
    food_preference = models.CharField(max_length=150)
    drink_option = models.ForeignKey(DrinkOption, blank=True, null=True, on_delete=models.SET_NULL)
    extra_option = models.ManyToManyField(ExtraOption, blank=True)
    other = models.CharField(max_length=300)

    def __str__(self):
        return str(self.user) + " anmäld till " + str(self.happening)