from django.contrib.auth import (
    login as django_login,
    logout as django_logout
)
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters

from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveUpdateAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response


from .utils import jwt_encode
from .models import UserProfile
from .serializers import JWTSerializer, JWTSerializerWithExpiration, LoginSerializer, RegisterOrganizationSerializer, UserSerializer, UserProfileSerializer
from django.contrib.admin.models import LogEntry

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters(
        'password', 'old_password', 'password1', 'password2'
    )
)

try:
    from allauth.account import app_settings as allauth_settings
    from allauth.account.utils import complete_signup

    from dj_rest_auth.registration.app_settings import register_permission_classes
    from dj_rest_auth.registration.views import RegisterView
    from dj_rest_auth.app_settings import (JWTSerializer, TokenSerializer,
                                           create_token)

except ImportError:
    print('Error import dj-rest-auth and dj-rest-auth.registration check if its installled in apps list')
# Views


class RegisterOrganizationView(RegisterView):
    serializer_class = RegisterOrganizationSerializer
    permission_classes = register_permission_classes()
    throttle_scope = 'dj_rest_auth'

    # def perform_create(self, serializer):
    #     user = serializer.save(self.request)
    #     if allauth_settings.EMAIL_VERIFICATION != \
    #             allauth_settings.EmailVerificationMethod.MANDATORY:
    #         if getattr(settings, 'REST_USE_JWT', False):
    #             self.access_token, self.refresh_token = jwt_encode(user)
    #         else:
    #             create_token(self.token_model, user, serializer)

    #     complete_signup(self.request._request, user,
    #                     allauth_settings.EMAIL_VERIFICATION,
    #                     None)
    #     return user

    # @sensitive_post_parameters_m
    # def dispatch(self, *args, **kwargs):
    #     return super(RegisterView, self).dispatch(*args, **kwargs)

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     user = self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)

    #     return Response(self.get_response_data(user),
    #                     status=status.HTTP_201_CREATED,
    #                     headers=headers)

    # def perform_create(self, serializer):
    #     user = serializer.save(self.request)
    #     if allauth_settings.EMAIL_VERIFICATION != \
    #             allauth_settings.EmailVerificationMethod.MANDATORY:
    #         if getattr(settings, 'REST_USE_JWT', False):
    #             self.access_token, self.refresh_token = jwt_encode(user)
    #         else:
    #             create_token(self.token_model, user, serializer)

    #     complete_signup(self.request._request, user,
    #                     allauth_settings.EMAIL_VERIFICATION,
    #                     None)
    #     return user


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


# class UserActivityView(viewsets.ReadonlyModelViewSet):
#     queryset = LogEntry.objects.all()
#     pass:


try:
    from dj_rest_auth.models import TokenModel
    from dj_rest_auth.registration.views import RegisterView as DJ_RestRegisterView
except ImportError:
    print('Failed to import files')

# class RegisterView(DJ_RestRegisterView):
#     serializer_class = RegisterSerializer
#     permission_classes = register_permission_classes()
#     token_model = TokenModel
