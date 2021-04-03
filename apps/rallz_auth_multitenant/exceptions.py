from drf_problems.utils import register
from rest_framework import exceptions


@register
class InvalidTenantException(exceptions.NotAcceptable):
    default_code = 'invalid_tenant'
    title = 'Invalid Tenant'
    default_detail = 'Provided Tenant is invalid.'
    description = 'Malformed or unsupported tenant value was provided with the request.'


@register
class InvalidUserException(exceptions.NotFound):
    default_code = 'invalid_user'
    title = 'Invalid User'
    default_detail = 'Provided User is invalid.'
    description = 'Malformed or unsupported user value was provided.'
