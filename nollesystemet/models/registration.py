from django.conf import settings
from django.db import models

from nollesystemet.models import Happening, DrinkOption, ExtraOption

class Registration(models.Model):

    happening = models.ForeignKey(Happening, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.USER_PROFILE_MODEL, on_delete=models.CASCADE)
    food_preference = models.CharField(max_length=150)
    drink_option = models.ForeignKey(DrinkOption, blank=True, null=True, on_delete=models.SET_NULL)
    extra_option = models.ManyToManyField(ExtraOption, blank=True)
    other = models.CharField(max_length=300)

    def __str__(self):
        try:
            return str(self.user) + " anmäld till " + str(self.happening)
        except:
            return super().__str__()

    def user_can_edit_registration(self, user_profile):
        return user_profile.auth_user.has_perm('edit_user_registration') \
               or user_profile in self.happening.editors.all() \
               or user_profile.auth_user.is_superuser

    def user_can_see_registration(self, user_profile):
        return user_profile == self.user or self.user_can_edit_registration(user_profile)
