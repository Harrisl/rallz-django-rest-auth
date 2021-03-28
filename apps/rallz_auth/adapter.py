from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from . import exceptions as auth_exceptions


class DefaultAccountAdapter(object):

    error_messages = {
        "username_blacklisted": _(
            "Username can not be used. Please use other username."
        ),
        "too_many_login_attempts": _(
            "Too many failed login attempts. Try again later."
        ),
        "email_taken": _("A user is already registered with this e-mail address."),
    }

    def __init__(self, request=None):
        self.request = request

    def stash_verified_email(self, request, email):
        request.session["account_verified_email"] = email

    def unstash_verified_email(self, request):
        ret = request.session.get("account_verified_email")
        request.session["account_verified_email"] = None
        return ret

    def stash_user(self, request, user):
        request.session["account_user"] = user

    def unstash_user(self, request):
        return request.session.pop("account_user", None)

    def is_email_verified(self, request, email):
        """
        Checks whether or not the email address is already verified
        beyond allauth scope, for example, by having accepted an
        invitation before signing up.
        """
        ret = False
        verified_email = request.session.get("account_verified_email")
        if verified_email:
            ret = verified_email.lower() == email.lower()
        return ret

    def new_user(self, request):
        """
        Instantiates a new User instance.
        """
        user = get_user_model()()
        return user

    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the
        signup form.
        """
        from .utils import user_email, user_field

        data = form.cleaned_data
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        user_email(user, email)
        if first_name:
            user_field(user, "first_name", first_name)
        if last_name:
            user_field(user, "last_name", last_name)
        if "password1" in data:
            user.set_password(data["password1"])
        else:
            user.set_unusable_password()
        # self.populate_username(request, user)
        if commit:
            # Ability not to commit makes it easier to derive from
            # this adapter by adding
            user.save()
        return user

    def validate_unique_email(self, email):
        if email_address_exists(email):
            raise auth_exceptions.EmailExistsException(
                self.error_messages["email_taken"])
        return email

    def confirm_email(self, request, email_address):
        """
        Marks the email address as confirmed on the db
        """
        email_address.verified = True
        email_address.set_as_primary(conditional=True)
        email_address.save()

    def set_password(self, user, password):
        user.set_password(password)
        user.save()

    def is_safe_url(self, url):
        try:
            from django.utils.http import url_has_allowed_host_and_scheme
        except ImportError:
            from django.utils.http import (
                is_safe_url as url_has_allowed_host_and_scheme,
            )

        return url_has_allowed_host_and_scheme(url, allowed_hosts=None)

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        pass


def get_adapter(request=None):
    return DefaultAccountAdapter(request)
