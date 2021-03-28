from drf_problems.utils import register_exception, register
from rest_framework import exceptions
# from common.exceptions import DetailDictMixin

# register_exception(InvalidVersionRequestedException) # Or this method directly.


@register
class InvalidVersionRequestedException(exceptions.NotAcceptable):
    default_code = 'invalid_version'
    title = 'Invalid API version'
    default_detail = 'Provided API version is invalid.'
    description = 'Malformed or unsupported version string is provided with the request.'


@register
class EmailExistsException(exceptions.ParseError):
    default_code = 'email_exists'
    title = 'Email exists'
    default_detail = 'This email already exists'
    description = 'This email address is already in use.'


@register
class UnverifiedEmailException(exceptions.AuthenticationFailed):
    """
    A verified email is required for the specified action. For example a multi-factor user.\n
    Requires a verified email.
    """
    default_code = 'unverified_email'
    title = 'Unverified Email '
    default_detail = 'E-mail is not verified.'
    description = 'This email not verified.'


@register
class UserDisabledException(exceptions.AuthenticationFailed):
    default_code = 'user_disabled'
    title = 'User Disabled'
    default_detail = 'This user is disabled'
    description = 'This user account is been disabled.'


@register
class InvalidPasswordException(exceptions.ParseError):
    default_code = 'Invalid_password'
    title = 'Invalid Password'
    default_detail = 'Password is invalid'
    description = 'This password is invalid.'

# @register
# class AuthenticationFailed(DetailDictMixin, exceptions.AuthenticationFailed):
#     pass
