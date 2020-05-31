from django.conf import settings
from django.db import models
from nollesystemet.models.happening import Happening, DrinkOption, ExtraOption


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