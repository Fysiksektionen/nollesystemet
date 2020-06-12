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

    def get_base_price(self):
        return self.happening.get_baseprice(self)

    def get_drink_option_price(self):
        if self.drink_option:
            return self.drink_option.price
        else:
            return 0

    def get_extra_option_price(self):
        return sum([values['price'] for values in self.extra_option.values('price')])

    def get_full_price(self):
        return self.get_base_price() + self.get_drink_option_price() + self.get_extra_option_price()

    @property
    def all_extra_options_str(self):
        return [str(extra_option) for extra_option in self.extra_option.all()]

