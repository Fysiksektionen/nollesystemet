from distutils.util import strtobool

from rest_framework import serializers, status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.filters import SearchFilter, BaseFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response

from nollesystemet.models import Registration


class RegistrationSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Registration
        fields = ['id', 'name', 'price', 'OCR', 'confirmed', 'paid', 'attended']

    def get_name(self, obj: Registration):
        return str(obj.user)

    def get_price(self, obj: Registration):
        return "%d,00 kr" % obj.pre_paid_price + \
               (" (+%d,00 kr)" % obj.on_site_paid_price if obj.on_site_paid_price else "")


class ShowPaidRegistationsFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        try:
            if 'show_paid' in request.GET and bool(strtobool(request.GET['show_paid'])):
                return queryset
        except ValueError:
            pass

        return queryset.filter(paid=False)


class ShowNonConfirmedRegistationsFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        try:
            if 'show_nonconfirmed' in request.GET and not bool(strtobool(request.GET['show_nonconfirmed'])):
                return queryset.filter(confirmed=True)
        except ValueError:
            pass

        return queryset


class ShowAttendedRegistationsFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        try:
            if 'show_attended' in request.GET and not bool(strtobool(request.GET['show_attended'])):
                return queryset.filter(attended=False)
        except ValueError:
            pass

        return queryset


class HappeningFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        try:
            if 'happening_id' in request.GET:
                return queryset.filter(happening__pk=int(request.GET['happening_id']))
        except:
            pass

        return queryset


class PaymentHandlingAllowed(BasePermission):
    def has_permission(self, request, view):
        return True


class RegistrationList(ListAPIView):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [IsAuthenticated, PaymentHandlingAllowed]
    filter_backends = [
        SearchFilter,
        ShowPaidRegistationsFilter,
        ShowNonConfirmedRegistationsFilter,
        ShowAttendedRegistationsFilter,
        HappeningFilter
    ]
    search_fields = ['^user__first_name', '^user__last_name', '^OCR']


class AlterRegistration(BasePermission):
    def has_permission(self, request, view):
        return True


@api_view(['POST'])
@permission_classes([IsAuthenticated, AlterRegistration])
def update_registration(request, pk, format=None):
    allowed_keys = ['paid', 'attended']

    for key in request.data:
        if key not in allowed_keys:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    update_kwargs = {}

    if 'paid' in request.data:
        update_kwargs['paid'] = bool(request.data['paid'])
    if 'attended' in request.data:
        update_kwargs['attended'] = bool(request.data['attended'])

    if len(update_kwargs) > 0:
        Registration.objects.filter(pk=pk).update(**update_kwargs)

    return Response(status=status.HTTP_202_ACCEPTED)


@api_view(['POST'])
@permission_classes([IsAuthenticated, AlterRegistration])
def confirm_registration(request, pk, format=None):
    try:
        registration = Registration.objects.get(pk=pk)
        if not registration.send_confirmation_email():
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Registration.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    return Response(status=status.HTTP_202_ACCEPTED)



