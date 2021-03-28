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
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .utils import jwt_encode
from .models import UserProfile
from .serializers import JWTSerializer, JWTSerializerWithExpiration, LoginSerializer, UserSerializer, UserProfileSerializer
from django.contrib.admin.models import LogEntry

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters(
        'password', 'old_password', 'new_password1', 'new_password2'
    )
)
# Views
@api_view()
@permission_classes([AllowAny])
def complete_view(request):
    return Response("Email account is activated")

@api_view()
@permission_classes([AllowAny])
def null_view(request):
    return Response(status=status.HTTP_400_BAD_REQUEST)

class LoginView(GenericAPIView):
    """
    Check the credentials and return the REST Token
    if the credentials are valid and authenticated.
    Calls Django Auth login method to register User ID
    in Django session framework

    Accept the following POST parameters: username, password
    Return the REST Framework Token Object's key.
    """
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(LoginView, self).dispatch(*args, **kwargs)

    def process_login(self):
        django_login(self.request, self.user)

    def get_response_serializer(self):
        # if getattr(settings, 'REST_USE_JWT', False):
        # response_serializer = JWTSerializer
        # if getattr(settings, 'JWT_AUTH_RETURN_EXPIRATION', False):
        response_serializer = JWTSerializerWithExpiration
        # else:
        # response_serializer = JWTSerializer
        # else:
        #     response_serializer = TokenSerializer
        return response_serializer

    def login(self):
        self.user = self.serializer.validated_data['user']

        # if getattr(settings, 'REST_USE_JWT', False):
        self.access_token, self.refresh_token = jwt_encode(self.user)

        # if getattr(settings, 'REST_SESSION_LOGIN', True):
        self.process_login()
        # return self.user

    def get_response(self):
        serializer_class = self.get_response_serializer()

        access_token_expiration = None
        refresh_token_expiration = None

        from rest_framework_simplejwt.settings import api_settings as jwt_settings
        access_token_expiration = (
            timezone.now() + jwt_settings.ACCESS_TOKEN_LIFETIME)
        refresh_token_expiration = (
            timezone.now() + jwt_settings.REFRESH_TOKEN_LIFETIME)
        # return_expiration_times = getattr(
        #     settings, 'JWT_AUTH_RETURN_EXPIRATION', True)

        data = {
            'user': self.user,
            'access_token': self.access_token,
            'refresh_token': self.refresh_token
        }

        # if return_expiration_times:
        data['access_token_expiration'] = access_token_expiration
        data['refresh_token_expiration'] = refresh_token_expiration

        serializer = serializer_class(instance=data,
                                      context=self.get_serializer_context())

        response = Response(serializer.data, status=status.HTTP_200_OK)
        # if getattr(settings, 'REST_USE_JWT', False):
        from .jwt_auth import set_jwt_cookies
        set_jwt_cookies(response, self.access_token, self.refresh_token)
        return response

    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)
        self.serializer.is_valid(raise_exception=True)

        self.login()
        return self.get_response()


class LogoutView(APIView):
    """
    Calls Django logout method and delete the Token object
    assigned to the current User object.

    Accepts/Returns nothing.
    """
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        return self.logout(request)

    def logout(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            pass
        # if getattr(settings, 'REST_SESSION_LOGIN', True):
        django_logout(request)

        response = Response({"detail": _("Successfully logged out.")},
                            status=status.HTTP_200_OK)
        # if getattr(settings, 'REST_USE_JWT', False):
        from rest_framework_jwt.settings import api_settings as jwt_settings
        if jwt_settings.JWT_AUTH_COOKIE:
            response.delete_cookie(jwt_settings.JWT_AUTH_COOKIE)
        return response


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
