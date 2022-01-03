from django.views.generic import TemplateView

from nollesystemet import mixins
from nollesystemet.api_views.campussafari import CheckSideQuestForGroup
from nollesystemet.models.campussafari import *


class FadderietCampussafariGrupperView(mixins.FadderietMixin, TemplateView):
    template_name = "fadderiet/campussafari/leaderboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'groups': sorted(CampusSafariGroup.objects.all(), key=lambda group: group.total_points, reverse=True)
        })
        return context


class FohserietStationAdministration(mixins.FohserietMixin, TemplateView):
    template_name = "fohseriet/campussafari/stationer.html"

    def test_func(self):
        try:
            return self.request.user.profile\
                .campus_safari_stations\
                .all()\
                .exists()
        except Exception:
            return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        groups = CampusSafariGroup.objects.all()
        stations = CampusSafariStation.objects.all()

        stations_w_points_per_group = []

        for group in groups:
            stations_w_points_for_group = []
            for station in stations:
                try:
                    points = CampusSafariStationPoints.objects.get(station_id=station.id, group_id=group.id).points
                except:
                    points = 0

                stations_w_points_for_group.append({
                    'station': station,
                    'points': points
                })

            stations_w_points_per_group.append({
                'group': group,
                'stations_w_points': stations_w_points_for_group
            })

        context.update({
            'stations_w_points_per_group': stations_w_points_per_group
        })
        return context


class FohserietSideQuestAdministration(mixins.FohserietMixin, TemplateView):
    template_name = "fohseriet/campussafari/sidouppdrag.html"

    def test_func(self):
        try:
            return self.request.user.profile\
                .campus_safari_groups\
                .all()\
                .exists()
        except Exception:
            return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        editable_groups = self.request.user.profile\
                              .campus_safari_groups\
                              .all()
        all_quests = CampusSafariSideQuest.objects.all()
        groups_data = [
            {
                'group': group,
                'side_quests': [{
                    'quest': quest,
                    'checked': quest.pk in group.side_quests.all().values_list('pk', flat=True)
                } for quest in all_quests]
            }
            for group in editable_groups
        ]

        context.update({
            'groups_data': groups_data
        })
        return context
