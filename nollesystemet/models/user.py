from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import gettext_lazy as _

import authentication.models as auth_models

class NolleGroup(models.Model):
    """
    Model for "nØllegrupper". Also contains extra information on the group itself.
    """
    name = models.CharField(verbose_name="Namn", max_length=150, unique=True, null=False, blank=False)
    description = models.TextField(max_length=1000, blank=True)
    logo = models.ImageField(null=True, blank=True)
    schedule = models.ImageField(null=True, blank=True)
    forfadders = models.ManyToManyField('UserProfile', blank=True, related_name='responsible_nolle_group')

    def __str__(self):
        return str(self.name)

    @staticmethod
    def is_forfadder(user):
        return NolleGroup.objects.filter(forfadders=user).count() > 0

    @staticmethod
    def get_forfadder_group(user, accept_multiple=False):
        if NolleGroup.is_forfadder(user):
            if accept_multiple:
                return NolleGroup.objects.filter(forfadders=user)
            else:
                return NolleGroup.objects.get(forfadders=user)
        else:
            return None


class UserProfile(auth_models.UserProfile):
    """
    Customized UserProfile model for nollesystemet. Defines all info relevant about a user.
    Objects of this model should be the model to interact with form other model in nollessytemet,
    like Happening and Registration.
    """
    class UserType(models.IntegerChoices):
        """
        Enum type for choices of UserProfile.user_type
        """
        FADDER = 1, _("Fadder")
        NOLLAN = 2, _("nØllan")
        SENIOR = 3, _("Senior")
        EXTERNAL = 4, _("Extern")

    class Program(models.IntegerChoices):
        """
        Enum type for choices of UserProfile.user_type
        """
        CTFYS = 1, _("Teknisk fysik")
        CTMAT = 2, _("Teknisk matematik")

    user_type = models.PositiveSmallIntegerField(verbose_name="Användartyp",
                                                 choices=UserType.choices, blank=True, null=True)
    nolle_group = models.ForeignKey(NolleGroup, verbose_name="nØllegrupp", blank=True, null=True,
                                    on_delete=models.SET_NULL)

    program = models.PositiveSmallIntegerField(blank=True, null=True, choices=Program.choices, editable=False)

    kth_id = models.CharField(max_length=20, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    food_preference = models.CharField(max_length=150, blank=True)
    contact_name = models.CharField(max_length=100, blank=True)
    contact_relation = models.CharField(max_length=100, blank=True)
    contact_phone_number = models.CharField(max_length=15, blank=True)

    class Meta(auth_models.UserProfile.Meta):
        permissions = [
            ("see_users", "Can see any user profile"),
            ("edit_users", "Can edit any user profile"),
        ]

    def has_perm(self, codename):
        return self.auth_user.has_perm(codename)

    def can_be_seen_by(self, observing_user):
        if self.can_be_edited_by(observing_user):                  # Has permission to edit the user
            return True
        if NolleGroup.is_forfadder(observing_user):             # Is forfadder for the user
            if self.nolle_group in NolleGroup.get_forfadder_group(observing_user, accept_multiple=True):
                return True
        if observing_user.has_perm('see_users'):                # Has correct permission
            return True
        return False

    def can_be_edited_by(self, observing_user):
        if observing_user == self:                      # Is their own profile
            return True
        if observing_user.has_perm('edit_users'):       # Has correct permission
            return True
        return False

    def can_see_some_user(self):
        # If can see more than one user. Larger than 1 because all users can see their own profile
        return len([user.can_be_seen_by(self) for user in UserProfile.objects.all()]) > 1

    def can_edit_some_user(self):
        # If can edit more than one user. Larger than 1 because all users can edit their own profile
        return len([user.can_be_edited_by(self) for user in UserProfile.objects.all()]) > 1

    def is_responsible_forfadder(self, potential_forfadder):
        if not NolleGroup.is_forfadder(potential_forfadder):
            return False
        else:
            return self.nolle_group in NolleGroup.get_forfadder_group(potential_forfadder, accept_multiple=True)
