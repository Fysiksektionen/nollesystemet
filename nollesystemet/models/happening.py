from django.conf import settings
from django.db import models
from django.db.models import Q

import authentication.models as auth_models


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
        return "%s (+%d kr)" % (self.group, self.base_price)


class DrinkOption(models.Model):
    happening = models.ForeignKey(Happening, on_delete=models.CASCADE)
    drink = models.CharField(max_length=30)
    price = models.IntegerField()

    def __str__(self):
        return "%s (+%d kr)" % (self.drink, self.price)


class ExtraOption(models.Model):
    happening = models.ForeignKey(Happening, on_delete=models.CASCADE)
    extra_option = models.CharField(max_length=30)
    price = models.IntegerField()

    def __str__(self):
        return "%s (+%d kr)" % (self.extra_option, self.price)