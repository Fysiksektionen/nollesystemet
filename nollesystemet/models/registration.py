from django.conf import settings
from django.db import models

from .happening import Happening, DrinkOption, ExtraOption
from .user import UserProfile

class Registration(models.Model):
    """ Model representing a registration of a user to a happening. Contains information on options and alike. """

    happening = models.ForeignKey(Happening, on_delete=models.CASCADE, editable=False)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, editable=False)
    food_preference = models.CharField(max_length=150)
    drink_option = models.ForeignKey(DrinkOption, blank=True, null=True, on_delete=models.SET_NULL)
    extra_option = models.ManyToManyField(ExtraOption, blank=True)
    other = models.CharField(max_length=300, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    paid = models.BooleanField(editable=False, default=False)
    attended = models.BooleanField(editable=False, default=False)

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

    @staticmethod
    def can_see_some(observing_user: UserProfile):
        """ :return Boolean indicating if observing_user has the right to see the registration of some user. """
        # If can see more than one user. Larger than 1 because all users can see their own profile
        return len([True for registration in Registration.objects.all() if registration.can_see(observing_user)]) > \
               len(Registration.objects.filter(user=observing_user))

    def can_edit(self, observing_user: UserProfile):
        if observing_user.has_perm('nollesystemet.edit_registration'):
            return True
        if self.happening.can_edit(observing_user):
            return True
        return False

    @staticmethod
    def can_edit_some(observing_user: UserProfile):
        """ :return Boolean indicating if observing_user has the right to see the registration of some user. """
        # If can see more than one user. Larger than 1 because all users can see their own profile
        return len([True for registration in Registration.objects.all()
                    if registration.can_edit(observing_user)]) > 0

    @property
    def base_price(self):
        return self.happening.get_baseprice(self)

    @property
    def drink_price(self):
        if self.drink_option:
            return self.drink_option.price
        else:
            return 0

    @property
    def extra_option_price(self):
        return sum([values['price'] for values in self.extra_option.values('price')])

    @property
    def pre_paid_price(self):
        if self.happening.include_drink_in_price:
            return self.base_price + self.extra_option_price + self.drink_price
        else:
            return self.base_price + self.extra_option_price

    @property
    def on_site_paid_price(self):
        if self.happening.include_drink_in_price:
            return None
        else:
            return self.drink_price

    @property
    def all_extra_options_str(self):
        return [str(extra_option) for extra_option in self.extra_option.all()]

