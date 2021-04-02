from django.contrib.auth.middleware import get_user
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject
from django_multitenant.utils import set_current_tenant
from rest_framework_simplejwt.authentication import JWTAuthentication

# from rest_framework_jwt.authentication import JSONWebTokenAuthentication


def get_tenant_for_user(user):
    return user.organization.tenantorganization


class AuthenticationMiddlewareTenant(MiddlewareMixin):
    # def process_request(self, request):
    #     assert hasattr(request, 'session'), (
    #         "The Django authentication middleware requires session middleware "
    #         "to be installed. Edit your MIDDLEWARE setting to insert "
    #         "'django.contrib.sessions.middleware.SessionMiddleware' before "
    #         "'django.contrib.auth.middleware.AuthenticationMiddleware'."
    #     )
    #     request.user = SimpleLazyObject(lambda: get_user(request))

    # def __init__(self, get_response):
    #     self.get_response = get_response

    # def __call__(self, request):
    #     if request.user and not request.user.is_anonymous:
    #         set_current_tenant(request.user.employee.company)
    #     return self.get_response(request)

    def process_request(self, request):
        request.user = SimpleLazyObject(
            lambda: self.__class__.get_request_user(request))

        # print(request.user.organization)

        if request.user.is_authenticated:
            if not request.user.is_staff:
                current_tenant = get_tenant_for_user(request.user)
                set_current_tenant(current_tenant)

    def process_response(self, request, response):
        set_current_tenant(None)

        return response

    @staticmethod
    def get_request_user(request):
        user = get_user(request)

        if user.is_authenticated:
            return user

        # Check if request uses jwt authentication
        jwt_authentication = JWTAuthentication()
        # if jwt_authentication.get_jwt_value(request):
        user, _ = jwt_authentication.authenticate(request)
        return user
