from drf_problems.utils import register
from rest_framework import exceptions

# register_exception(InvalidVersionRequestedException) # Or this method directly.


class DetailDictMixin:
    def __init__(self, detail=None, code=None):
        """
        Builds a detail dictionary for the error to give more information to API
        users.
        """
        detail_dict = {'detail': self.default_detail,
                       'code': self.default_code}

        if isinstance(detail, dict):
            detail_dict.update(detail)
        elif detail is not None:
            detail_dict['detail'] = detail

        if code is not None:
            detail_dict['code'] = code

        super().__init__(detail_dict)


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


class AuthenticationFailed(DetailDictMixin, exceptions.AuthenticationFailed):
    #     pass

    # class DetailDictMixin:
    def __init__(self, detail=None, code=None):
        """
        Builds a detail dictionary for the error to give more information to API
        users.
        """
        detail_dict = {'detail': self.default_detail,
                       'code': self.default_code}

        if isinstance(detail, dict):
            detail_dict.update(detail)
        elif detail is not None:
            detail_dict['detail'] = detail

        if code is not None:
            detail_dict['code'] = code

        super().__init__(detail_dict)


# class AuthenticationFailed(DetailDictMixin, exceptions.AuthenticationFailed):
    # pass


class OwnershipRequired(exceptions.APIException):
    # status_code = status.HTTP_400_BAD_REQUEST
    # default_detail = _('Malformed request.')
    # default_code = 'parse_error'
    """
    Exception to raise if the owner is being removed before the
    organization.
    """

    pass


class OrganizationMismatch(exceptions.APIException):
    """
    Exception to raise if an organization user from a different
    organization is assigned to be an organization's owner.
    """

    pass
