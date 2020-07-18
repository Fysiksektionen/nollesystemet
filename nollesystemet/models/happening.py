from django.apps import apps
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

import authentication.models as auth_models
from .user import UserProfile, NolleGroup
from .fields import MultipleChoiceEnumModelField

def _is_editor_condition():
    return {'pk__in': [user.pk for user in UserProfile.objects.all()
                       if user.auth_user.has_perm('nollesystemet.edit_happening')]}

class Happening(models.Model):
    """
    Model representing a physical (or digital) event.
    Stores information on the event and available options at a registration.
    """

    class HappeningStatus(models.IntegerChoices):
        """
        Enum type for status of a happening.
        """
        UNPUBLISHED = 1, _("Ej publicerad")
        PUBLISHED = 2, _("Publicerad")
        OPEN = 3, _("Öppen för anmälan")
        CLOSED = 4, _("Stängd för anmälan")
        COMPLETED = 5, _("Genomfört")

    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=300)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    image_file_path = models.CharField(max_length=50)
    food = models.BooleanField(default=True)

    takes_registration = models.BooleanField(default=False)
    status = models.PositiveSmallIntegerField(choices=HappeningStatus.choices,
                                              default=HappeningStatus.UNPUBLISHED)
    user_types = MultipleChoiceEnumModelField(UserProfile.UserType, blank=False, null=False,
                                              default=[UserProfile.UserType.NOLLAN, UserProfile.UserType.FADDER])
    nolle_groups = models.ManyToManyField(NolleGroup, related_name="happening_nolle_group")

    editors = models.ManyToManyField(UserProfile, limit_choices_to=_is_editor_condition)

    class Meta(auth_models.UserProfile.Meta):
        permissions = [
            ("create_happening", "Can create happenings"),
            ("edit_happening", "Can edit any happening"),
        ]

    def __str__(self):
        return str(self.name)

    @staticmethod
    def can_create(observing_user: UserProfile):
        return observing_user.has_perm('nollesystemet.create_happening')

    def can_attend(self, observing_user: UserProfile):
        return observing_user.user_type in self.user_types and \
               (observing_user.nolle_group in self.nolle_groups.all() or
                self.nolle_groups.all().count() == NolleGroup.objects.all().count())

    def can_register(self, observing_user: UserProfile):
        return self.is_open_for_registration() and self.can_attend(observing_user)

    @staticmethod
    def can_register_to_some(observing_user: UserProfile):
        return len([True for happening in Happening.objects.all()
                    if happening.can_register(observing_user)]) > 0

    def can_see_registered(self, observing_user: UserProfile):
        return self.can_edit(observing_user) or \
               observing_user.has_perm('nollesystemet.see_registration') or \
               observing_user.has_perm('nollesystemet.edit_registration')

    @staticmethod
    def can_see_some_registered(observing_user: UserProfile):
        return len([True for happening in Happening.objects.all()
                    if happening.can_see_registered(observing_user)]) > 0

    def can_edit(self, observing_user: UserProfile):
        return observing_user in self.editors.all() or observing_user.has_perm('nollesystemet.edit_happening')

    @staticmethod
    def can_edit_some_registered(observing_user: UserProfile):
        return len([True for happening in Happening.objects.all()
                    if happening.can_edit(observing_user)]) > 0

    def is_published(self):
        return self.status in [Happening.HappeningStatus.PUBLISHED,
                               Happening.HappeningStatus.OPEN,
                               Happening.HappeningStatus.CLOSED]

    def is_open_for_registration(self):
        return self.takes_registration and self.status == Happening.HappeningStatus.OPEN

    def has_closed(self):
        return self.status in [Happening.HappeningStatus.CLOSED, Happening.HappeningStatus.COMPLETED]

    def is_visible_to(self, user: UserProfile):
        return self.is_published() and self.can_attend(user)

    def is_registered(self, user: UserProfile):
        return apps.get_model('nollesystemet.Registration').objects.filter(happening=self, user=user).exists()

    def get_baseprice(self, registration):
        try:
            return self.usertypebaseprice_set.get(user_type=registration.user.user_type).price
        except UserTypeBasePrice.DoesNotExist:
            return 0


class UserTypeBasePrice(models.Model):
    """ Model representing the minimum price of a happening for a given UserProfile.UserType. """

    user_type = models.PositiveSmallIntegerField(choices=UserProfile.UserType.choices)
    happening = models.ForeignKey(Happening, on_delete=models.CASCADE)
    price = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ['happening', 'user_type']

    def __str__(self):
        return "%s (+%d kr)" % (self.user_type, self.price)


class DrinkOption(models.Model):
    """ Model representing an option of drinks to a happening and its associated price. """

    drink = models.CharField(max_length=30)
    happening = models.ForeignKey(Happening, on_delete=models.CASCADE)
    price = models.IntegerField()

    class Meta:
        unique_together = ['happening', 'drink']

    def __str__(self):
        return "%s (+%d kr)" % (self.drink, self.price)


class ExtraOption(models.Model):
    """ Model representing extra options of a happening and their respective price. """

    extra_option = models.CharField(max_length=30)
    happening = models.ForeignKey(Happening, on_delete=models.CASCADE)
    price = models.IntegerField()

    class Meta:
        unique_together = ['happening', 'extra_option']

    def __str__(self):
        return "%s (+%d kr)" % (self.extra_option, self.price)
