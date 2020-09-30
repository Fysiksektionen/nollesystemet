from django.apps import apps
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from multiselectfield import MultiSelectField

import authentication.models as auth_models
from .user import UserProfile, NolleGroup
from .misc import IntegerChoices, validate_no_emoji


def _is_editor_condition():
    return {'pk__in': [user.pk for user in UserProfile.objects.all()
                       if user.auth_user.has_perm('nollesystemet.edit_happening')]}
def _is_not_nollan():
    return ~models.Q(user_type=UserProfile.UserType.NOLLAN)


class Happening(models.Model):
    """
    Model representing a physical (or digital) event.
    Stores information on the event and available options at a registration.
    """

    class HappeningStatus(IntegerChoices):
        """
        Enum type for status of a happening.
        """
        UNPUBLISHED = 1, _("Ej publicerad")
        PUBLISHED = 2, _("Publicerad")
        OPEN = 3, _("Öppen för anmälan")
        CLOSED = 4, _("Stängd för anmälan")
        COMPLETED = 5, _("Genomfört")

    name = models.CharField(max_length=50, unique=True, validators=[validate_no_emoji])
    description = models.CharField(max_length=500, validators=[validate_no_emoji])
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    image_file_path = models.CharField(max_length=50, validators=[validate_no_emoji])
    food = models.BooleanField(default=True)

    takes_registration = models.BooleanField(default=False)
    status = models.PositiveSmallIntegerField(choices=HappeningStatus.choices,
                                              default=HappeningStatus.UNPUBLISHED)
    user_types = MultiSelectField(choices=UserProfile.UserType.choices, blank=True)
    nolle_groups = models.ManyToManyField(NolleGroup, related_name="happening_nolle_group")

    editors = models.ManyToManyField(UserProfile)

    contact_name = models.CharField(max_length=150, blank=False, null=False, validators=[validate_no_emoji])
    contact_phone = models.CharField(max_length=30, validators=[validate_no_emoji])
    contact_email = models.EmailField(blank=False, null=False, validators=[validate_no_emoji])

    location = models.CharField(max_length=200, blank=False, null=False, validators=[validate_no_emoji])

    include_drink_in_price = models.BooleanField(default=False)
    include_extra_in_price = models.BooleanField(default=True)
    automatic_confirmation = MultiSelectField(choices=UserProfile.UserType.choices, blank=True)

    exclusive_access = models.ManyToManyField(UserProfile, blank=True, limit_choices_to=_is_not_nollan,
                                              related_name='exclusive_access_happenings')

    class Meta(auth_models.UserProfile.Meta):
        permissions = [
            ("create_happening", "Can create happenings"),
            ("edit_happening", "Can edit any happening"),
        ]
        verbose_name = 'Evenemang'
        verbose_name_plural = 'Evenemang'

    def __str__(self):
        return str(self.name)

    @staticmethod
    def can_create(observing_user: UserProfile):
        return observing_user.has_perm('nollesystemet.create_happening')

    @staticmethod
    def user_is_editor(observing_user: UserProfile):
        return len([True for happening in Happening.objects.all() if observing_user in happening.editors.all()]) > 0

    def can_attend(self, observing_user: UserProfile):
        return self.has_exclusive_access(observing_user) or \
               (self.has_acceptable_user_type(observing_user) and
                (observing_user.nolle_group in self.nolle_groups.all() or
                 self.nolle_groups.all().count() == NolleGroup.objects.all().count()))

    def has_exclusive_access(self, observing_user: UserProfile):
        return observing_user in self.exclusive_access.all()

    def has_acceptable_user_type(self, observing_user: UserProfile):
        return observing_user.user_type in UserProfile.UserType.list_parse(self.user_types)

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

    @property
    def num_of_registered(self):
        return self.registration_set.count()

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

    def get_baseprice(self, argument):
        if isinstance(argument, apps.get_model('nollesystemet.Registration')):
            try:
                return self.usertypebaseprice_set.get(user_type=argument.user.user_type).price
            except UserTypeBasePrice.DoesNotExist:
                all_prices = self.usertypebaseprice_set.all().order_by('price')
                if len(all_prices) == 0:
                    return 0
                else:
                    return all_prices[len(all_prices) - 1].price
        elif isinstance(argument, apps.get_model('nollesystemet.UserProfile').UserType):
            try:
                return self.usertypebaseprice_set.get(user_type=argument).price
            except UserTypeBasePrice.DoesNotExist:
                all_prices = self.usertypebaseprice_set.all().order_by('price')
                if len(all_prices) == 0:
                    return 0
                else:
                    return all_prices[len(all_prices) - 1].price


class UserTypeBasePrice(models.Model):
    """ Model representing the minimum price of a happening for a given UserProfile.UserType. """

    user_type = models.PositiveSmallIntegerField(choices=UserProfile.UserType.choices)
    happening = models.ForeignKey(Happening, on_delete=models.CASCADE)
    price = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ['happening', 'user_type']
        verbose_name = 'Baspris'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s (+%d kr)" % (UserProfile.UserType(self.user_type).label, self.price)


class DrinkOption(models.Model):
    """ Model representing an option of drinks to a happening and its associated price. """

    drink = models.CharField(max_length=30, validators=[validate_no_emoji])
    happening = models.ForeignKey(Happening, on_delete=models.CASCADE)
    price = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ['happening', 'drink']
        verbose_name = 'Dryckesalternativ'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s (+%d kr)" % (self.drink, self.price)


class ExtraOption(models.Model):
    """ Model representing extra options of a happening and their respective price. """

    extra_option = models.CharField(max_length=30, validators=[validate_no_emoji])
    happening = models.ForeignKey(Happening, on_delete=models.CASCADE)
    price = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ['happening', 'extra_option']
        verbose_name = 'Tillval'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s (+%d kr)" % (self.extra_option, self.price)
