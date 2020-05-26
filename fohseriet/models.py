from django.conf import settings
from django.db import models

import authentication.models as auth_models


class UserProfile(auth_models.UserProfile):
    kth_id = models.CharField(max_length=20, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    food_preference = models.CharField(max_length=15, blank=True)
    contact_name = models.CharField(max_length=100, blank=True)
    contact_relation = models.CharField(max_length=100, blank=True)
    contact_phone_number = models.CharField(max_length=15, blank=True)


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

    has_base_price = models.BooleanField(default=False)
    food = models.BooleanField(default=True)
    cost_for_drinks = models.BooleanField(default=False)
    cost_for_extras = models.BooleanField(default=False)

    editors = models.ManyToManyField(settings.AUTH_USER_MODEL)


class GroupHappeningProperties(models.Model):
    group = models.ForeignKey(auth_models.UserGroup, on_delete=models.CASCADE)
    happening = models.ForeignKey(Happening, on_delete=models.CASCADE)
    base_price = models.IntegerField()


class DrinkOption(models.Model):
    happening = models.ForeignKey(Happening, on_delete=models.CASCADE)
    drink = models.CharField(max_length=30)
    price = models.IntegerField()


class ExtraOption(models.Model):
    happening = models.ForeignKey(Happening, on_delete=models.CASCADE)
    extra_option = models.CharField(max_length=30)
    price = models.IntegerField()

class Registration(models.Model):
    happening = models.ForeignKey(Happening, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    food_preference = models.CharField(max_length=50)
    drink_option = models.ForeignKey(DrinkOption, blank=True, null=True, on_delete=models.SET_NULL)
    extra_option = models.ManyToManyField(ExtraOption, blank=True)
    other = models.CharField(max_length=300)

