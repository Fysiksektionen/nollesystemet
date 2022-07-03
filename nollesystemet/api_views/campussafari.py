from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated, BasePermission, AllowAny
from rest_framework.response import Response

from nollesystemet.models.campussafari import *


class CheckSideQuestForGroup(BasePermission):
    def has_permission(self, request, view):
        try:
            return request.user.profile\
                .campus_safari_groups\
                .filter(pk=view.kwargs['group_pk'])\
                .exists()
        except:
            return False


@api_view(['POST'])
@permission_classes([IsAuthenticated, CheckSideQuestForGroup])
def check_side_quest(request, group_pk, side_pk, format=None):
    try:
        try:
            side_quest = CampusSafariSideQuest.objects.get(pk=side_pk)
        except CampusSafariSideQuest.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            group = CampusSafariGroup.objects.get(pk=group_pk)
        except CampusSafariGroup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            check = bool(request.data['check'])
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if check:
            group.side_quests.add(side_quest)
        else:
            group.side_quests.remove(side_quest)

        group.save()

    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(status=status.HTTP_202_ACCEPTED)


class SetStationPoints(BasePermission):
    def has_permission(self, request, view):
        try:
            return request.user.profile\
                .campus_safari_stations\
                .filter(pk=view.kwargs['station_pk'])\
                .exists()
        except:
            return False


@api_view(['POST'])
@permission_classes([IsAuthenticated, SetStationPoints])
def set_station_points(request, station_pk, group_pk, format=None):
    try:
        try:
            station_points = CampusSafariStationPoints.objects.get(station__pk=station_pk, group__pk=group_pk)
        except CampusSafariStationPoints.DoesNotExist:
            station_points = CampusSafariStationPoints()
            try:
                station_points.station = CampusSafariStation.objects.get(pk=station_pk)
            except CampusSafariStation.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            try:
                station_points.group = CampusSafariGroup.objects.get(pk=group_pk)
            except CampusSafariGroup.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            station_points.points = int(request.data['points'])
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        station_points.save()

    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(status=status.HTTP_202_ACCEPTED)
