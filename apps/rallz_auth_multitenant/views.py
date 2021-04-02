
import rest_framework


from rest_framework import viewsets
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import UserDetailsView

from apps.rallz_auth_multitenant.serializers import (
    RegisterOrganizationSerializer, TenantUserSerializer)

# Create your views here.


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
