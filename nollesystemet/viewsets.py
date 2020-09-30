from django.views.decorators.csrf import csrf_protect
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import api_view

from .models import UserProfile
from .serializers import UserProfileSerializer

@csrf_protect
@api_view(['GET', 'PUT', 'DELETE'])
def user_profile_detail_api_view(request, pk):
    """ Retrieve, update or delete a UserProfile. """
    if request.user.is_anonymous or not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    try:
        user_profile = UserProfile.objects.get(pk=pk)
    except UserProfile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        if request.method == 'GET':
            if user_profile.can_see(request.user.profile):
                serializer = UserProfileSerializer(user_profile)
                return Response(serializer.data)

        elif request.method == 'PUT':
            if user_profile.can_edit(request.user.profile):
                serializer = UserProfileSerializer(user_profile, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            if user_profile.can_edit(request.user.profile):
                user_profile.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

    except AttributeError:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
