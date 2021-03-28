from six import string_types
from importlib import import_module
from django.core.exceptions import FieldDoesNotExist, ValidationError
from .adapter import get_adapter


def import_callable(path_or_callable):
    if hasattr(path_or_callable, '__call__'):
        return path_or_callable
    else:
        assert isinstance(path_or_callable, str)
        package, attr = path_or_callable.rsplit('.', 1)
        return getattr(import_module(package), attr)


def jwt_encode(user):
    from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
    # rest_auth_serializers = getattr(settings, 'REST_AUTH_SERIALIZERS', {})

    # JWTTokenClaimsSerializer = rest_auth_serializers.get(
    #     'JWT_TOKEN_CLAIMS_SERIALIZER',
    #     TokenObtainPairSerializer
    # )

    # TOPS = import_callable(JWTTokenClaimsSerializer)

    refresh = TokenObtainPairSerializer.get_token(user)
    return refresh.access_token, refresh


def user_field(user, field, *args):
    """
    Gets or sets (optional) user model fields. No-op if fields do not exist.
    """
    if not field:
        return
    User = get_user_model()
    try:
        field_meta = User._meta.get_field(field)
        max_length = field_meta.max_length
    except FieldDoesNotExist:
        if not hasattr(user, field):
            return
        max_length = None
    if args:
        # Setter
        v = args[0]
        if v:
            v = v[0:max_length]
        setattr(user, field, v)
    else:
        # Getter
        return getattr(user, field)


def user_email(user, *args):
    return user_field(user, "email", *args)


# def setup_user_email(request, user, addresses):
#     """
#     Creates proper EmailAddress for the user that was just signed
#     up. Only sets up, doesn't do any other handling such as sending
#     out email confirmation mails etc.
#     """
#     from .models import EmailAddress

#     assert not EmailAddress.objects.filter(user=user).exists()
#     priority_addresses = []
#     # Is there a stashed e-mail?
#     adapter = get_adapter(request)
#     stashed_email = adapter.unstash_verified_email(request)
#     if stashed_email:
#         priority_addresses.append(
#             EmailAddress(user=user, email=stashed_email,
#                          primary=True, verified=True)
#         )
#     email = user_email(user)
#     if email:
#         priority_addresses.append(
#             EmailAddress(user=user, email=email, primary=True, verified=False)
#         )
#     addresses, primary = cleanup_email_addresses(
#         request, priority_addresses + addresses
#     )
#     for a in addresses:
#         a.user = user
#         a.save()
#     EmailAddress.objects.fill_cache_for_user(user, addresses)
#     if primary and email and email.lower() != primary.email.lower():
#         user_email(user, primary.email)
#         user.save()
#     return primary


# def email_address_exists(email, exclude_user=None):
#     # from .account import app_settings as account_settings
#     from .account.models import EmailAddress

#     emailaddresses = EmailAddress.objects
#     if exclude_user:
#         emailaddresses = emailaddresses.exclude(user=exclude_user)
#     ret = emailaddresses.filter(email__iexact=email).exists()
#     if not ret:
#         # email_field = account_settings.USER_MODEL_EMAIL_FIELD
#         email_field = "email"
#         # if email_field:
#         users = get_user_model().objects
#         if exclude_user:
#             users = users.exclude(pk=exclude_user.pk)
#         ret = users.filter(**{email_field + "__iexact": email}).exists()
#     return ret


# try:
#     from .jwt_auth import JWTCookieAuthentication
# except ImportError:
#     pass
