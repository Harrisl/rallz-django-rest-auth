import logging
from django.contrib.auth import get_user
from django.utils.functional import SimpleLazyObject
from django.utils.deprecation import MiddlewareMixin
from django_multitenant.utils import (get_current_tenant, unset_current_tenant,
                                      get_tenant_column, set_current_tenant)
import apps.rallz_auth_multitenant.exceptions as auth_exceptions
logger = logging.getLogger(__name__)


def get_request_user(request):
    if not hasattr(request, '_cached_user'):
        request._cached_user = get_user(request)
    return request._cached_user


def get_tenant_for_user(user):
    return user.organization


class MultitenantMiddleware(MiddlewareMixin):
    # def __init__(self, get_response):
    #     self.get_response = get_response
    #     super().__init__(get_response)

    # def __call__(self, request):
    #     if request.user and not request.user.is_anonymous:
    #         current_tenant = get_tenant_for_user(request.user)
    #         set_current_tenant(current_tenant)
    #         # return self.get_response(request)
    #         return super().__call__(request)

    # TODO: Looks like the request.user is already set maybe we can just use it w/o using the JwtAuthentication
    #       though for other users like mobile then wed have to use different token authentication

    def process_request(self, request):
        if not hasattr(self, 'authenticator'):

            from rest_framework_simplejwt.authentication import \
                JWTAuthentication
            # authenticator = JWTAuthentication()
            self.authenticator = JWTAuthentication()
            try:
                # uses token
                # user = authenticator.authenticate(request)
                user = self.authenticator.authenticate(request)
                if user is None:
                    # uses api browser from django session
                    # TODO: maybe should remove/improve as is uses 'AnonymousUser'
                    user = SimpleLazyObject(
                        lambda: get_request_user(request)) or request.user
                if user.is_anonymous is True:
                    raise auth_exceptions.InvalidUserException
            except:
                from rest_framework.authtoken.models import Token
                # Check if request uses Django auth token
                auth_header = request.META.get('HTTP_AUTHORIZATION')
                if auth_header and auth_header.find('Token') != -1:
                    keyword, token, = auth_header.split()
                    if keyword == 'Token':
                        try:
                            user = Token.objects.get(key=token).user
                            return user
                        except Token.DoesNotExist:
                            pass
            try:
                # Assuming your app has a function to get the tenant associated for a user
                # current_tenant = get_tenant_for_user(user)
                if user and not user.is_anonymous:
                    if(user.organization != get_current_tenant()):
                        unset_current_tenant()
                        set_current_tenant(user.organization)

                    print('get_current_tenant', get_current_tenant())

            except Exception as e:
                # TODO: handle failure
                logger.error('Unable to set tenant value '
                             'tenant not available on user')
                return

    def process_response(self, request, response):
        # set_current_tenant(None)
        unset_current_tenant()
        return response
