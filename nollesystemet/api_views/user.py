from crispy_forms.utils import render_crispy_form
from rest_framework.renderers import JSONRenderer

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes

from nollesystemet.forms import ProfileUpdateForm
from nollesystemet.models import UserProfile


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def get_user_profile_form_HTML(request, pk, format=None):
    """ Retrieve a form filled with user data. """

    if request.user.is_anonymous or not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    try:
        user_profile = UserProfile.objects.get(pk=pk)
    except UserProfile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        if user_profile.can_see(request.user.profile):
            return Response(data={
                'form_HTML': render_crispy_form(ProfileUpdateForm(instance=user_profile, editable=False))
            })
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
