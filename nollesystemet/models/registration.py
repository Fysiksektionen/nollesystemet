from django.conf import settings
from django.db import models

from .happening import Happening, DrinkOption, ExtraOption
from .user import UserProfile

class Registration(models.Model):
    """ Model representing a registration of a user to a happening. Contains information on options and alike. """

    happening = models.ForeignKey(Happening, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    food_preference = models.CharField(max_length=150)
    drink_option = models.ForeignKey(DrinkOption, blank=True, null=True, on_delete=models.SET_NULL)
    extra_option = models.ManyToManyField(ExtraOption, blank=True)
    other = models.CharField(max_length=300)

    class Meta:
        permissions = [
            ("see_registration", "Can see any registration"),
            ("edit_registration", "Can edit any registration"),
        ]

    def __str__(self):
        try:
            return str(self.user) + " anmäld till " + str(self.happening)
        except:
            return super().__str__()

    def can_see(self, observing_user: UserProfile):
        if observing_user == self.user:
            return True
        if self.can_edit(observing_user):
            return True
        if self.user.is_responsible_forfadder(observing_user):
            return True
        return False

    def can_edit(self, observing_user: UserProfile):
        if observing_user.has_perm('edit_registration'):
            return True
        if self.happening.can_edit(observing_user):
            return True
        return False

    def get_base_price(self):
        return self.happening.get_baseprice(self)

    def get_drink_option_price(self):
        if self.drink_option:
            return self.drink_option.price
        else:
            return 0

    def get_extra_option_price(self):
        return sum([values['price'] for values in self.extra_option.values('price')])

    def get_price(self):
        return self.get_base_price() + self.get_drink_option_price() + self.get_extra_option_price()

    @property
    def all_extra_options_str(self):
        return [str(extra_option) for extra_option in self.extra_option.all()]

