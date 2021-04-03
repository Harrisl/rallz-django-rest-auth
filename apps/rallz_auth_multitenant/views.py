
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import UserDetailsView
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

# Create your views here.
from apps.rallz_auth_multitenant.models import TenantOrganization
from apps.rallz_auth_multitenant.serializers import (
    OrganizationSerializerWithUsers, RegisterOrganizationSerializer,
    TenantUserSerializer)


@api_view()
@permission_classes([AllowAny])
def complete_view(request):
    return Response("Email account is activated")


@api_view()
@permission_classes([AllowAny])
def null_view(request):
    return Response(status=status.HTTP_400_BAD_REQUEST)


class OrganizationRegisterView(RegisterView):
    serializer_class = RegisterOrganizationSerializer


class OrganizationUserDetailsView(UserDetailsView):
    """
    Reads and updates UserModel fields
    Accepts GET, PUT, PATCH methods.

    Default accepted fields: username, first_name, last_name
    Default display fields: pk, username, email, first_name, last_name
    Read-only fields: pk, email

    Returns UserModel fields.
    """
    serializer_class = TenantUserSerializer


class TenantOrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    # class OrganizationViewSet(RetrieveUpdateAPIView):
    """
    Reads and updates UserModel fields
    Accepts GET, PUT, PATCH methods.

    Default accepted fields: username, first_name, last_name
    Default display fields: pk, username, email, first_name, last_name
    Read-only fields: pk, email

    Returns UserModel fields.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = OrganizationSerializerWithUsers

    def get_queryset(self):
        return TenantOrganization.objects.get_for_user(user=self.request.user)

    # @action(detail=True, methods=['put'], serializer_class=JobReportMediaSerializer)
