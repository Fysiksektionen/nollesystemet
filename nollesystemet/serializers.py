from authentication.models import AuthUser
from .models import UserProfile
from .forms import ProfileUpdateForm
from rest_framework import serializers
from crispy_forms.utils import render_crispy_form

class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    auth_user = AuthUserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = '__all__'

    def to_representation(self, instance):
        """ Add form HTML."""
        ret = super().to_representation(instance)
        ret['from_HMTL'] = render_crispy_form(ProfileUpdateForm(instance=instance, editable=False))
        return ret


