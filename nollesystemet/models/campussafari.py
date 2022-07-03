from django.db import models

from .misc import validate_no_emoji
from .user import UserProfile


class CampusSafariSideQuest(models.Model):
    class Meta:
        verbose_name = 'Campus Safari-sidouppdrag'
        verbose_name_plural = 'Campus Safari-sidouppdrag'

    name = models.CharField(max_length=50, unique=True, validators=[validate_no_emoji], null=False, blank=False)
    points = models.PositiveIntegerField(null=False, blank=False)

    def __str__(self):
        return self.name + " (%d p)" % self.points


class CampusSafariStation(models.Model):
    class Meta:
        verbose_name = 'Campus Safari-station'
        verbose_name_plural = 'Campus Safari-stationer'

    name = models.CharField(max_length=50, unique=True, validators=[validate_no_emoji], null=False, blank=False)
    responsible = models.ManyToManyField(
        UserProfile,
        related_name="campus_safari_stations",
        limit_choices_to={
            'user_type__in': [UserProfile.UserType.FADDER,
                              UserProfile.UserType.FORFADDER,
                              UserProfile.UserType.ADMIN]
        }
    )

    def __str__(self):
        return self.name


class CampusSafariGroup(models.Model):
    class Meta:
        verbose_name = 'Campus Safari-grupp'
        verbose_name_plural = 'Campus Safari-grupper'

    name = models.CharField(max_length=50, unique=True, validators=[validate_no_emoji], null=False, blank=False)
    responsible_fadders = models.ManyToManyField(
        UserProfile,
        related_name="campus_safari_groups",
        limit_choices_to={
            'user_type__in': [UserProfile.UserType.FADDER,
                              UserProfile.UserType.FORFADDER,
                              UserProfile.UserType.ADMIN]
        }
    )

    side_quests = models.ManyToManyField(CampusSafariSideQuest, related_name="successful_groups", blank=True)

    @property
    def total_points(self):
        side_quest_points = sum(self.side_quests.values_list('points', flat=True))
        station_points = sum(self.station_points.values_list('points', flat=True))
        return side_quest_points + station_points

    def __str__(self):
        return self.name


class CampusSafariStationPoints(models.Model):
    station = models.ForeignKey(CampusSafariStation, on_delete=models.CASCADE, related_name='group_points', null=False, blank=False)
    group = models.ForeignKey(CampusSafariGroup, on_delete=models.CASCADE, related_name='station_points', null=False, blank=False)
    points = models.PositiveIntegerField(null=False, blank=False, default=0)
