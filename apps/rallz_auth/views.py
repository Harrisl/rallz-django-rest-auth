# from django.contrib.auth import (
#     login as django_login,
#     logout as django_logout
# )
# from django.conf import settings
# from django.contrib.auth import get_user_model
# from django.contrib.admin.models import LogEntry
# from django.core.exceptions import ObjectDoesNotExist
# from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
# from rest_framework.views import APIView
# CreateAPIView, GenericAPIView, , RetrieveAPIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Organization, UserProfile
from .serializers import OrganizationSerializerWithUsers, UserProfileSerializer, UserSerializer

# from organizations.models import Organization, OrganizationUser

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters(
        'password', 'old_password', 'password1', 'password2'
    )
)

# try:
# from allauth.account import app_settings as allauth_settings
# from allauth.account.utils import complete_signup

# from dj_rest_auth.registration.app_settings import register_permission_classes
# from dj_rest_auth.registration.views import RegisterView
# from dj_rest_auth.app_settings import (JWTSerializer, TokenSerializer,
#                                        create_token)

# except ImportError:
#     print('Error import dj-rest-auth and dj-rest-auth.registration check if its installled in apps list')
# Views


@api_view()
@permission_classes([AllowAny])
def complete_view(request):
    return Response("Email account is activated")


@api_view()
@permission_classes([AllowAny])
def null_view(request):
    return Response(status=status.HTTP_400_BAD_REQUEST)


class UserDetailsView(RetrieveUpdateAPIView):
    """
    Reads and updates UserModel fields
    Accepts GET, PUT, PATCH methods.

    Default accepted fields: username, first_name, last_name
    Default display fields: id, username, email, first_name, last_name
    Read-only fields: id, email

    Returns UserModel fields.
    """
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class UserProfileDetailsView(RetrieveUpdateAPIView):
    """
    Reads and updates UserProfile fields
    Accepts GET, PUT, PATCH methods.

    Default accepted fields: username, first_name, last_name
    # Default display fields: id, username, email, first_name, last_name
    Read-only fields: user, email

    Returns UserProfile fields.
    """
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return get_object_or_404(UserProfile, user=self.request.user)


class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
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
        return Organization.objects.get_for_user(user=self.request.user)

    # def get_object(self):
    #     return self.request.user.organization
        # return get_object_or_404(Organization, user=self.request.user)
        # return Organization.objects.get_for_user(user=self.request.user).first()
        #


# class UserActivityView(viewsets.ReadonlyModelViewSet):
#     queryset = LogEntry.objects.all()
#     pass:
