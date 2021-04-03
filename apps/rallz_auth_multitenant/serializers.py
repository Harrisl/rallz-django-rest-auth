# import logging

# from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions, serializers

from apps.rallz_auth import \
    exceptions as auth_exceptions  # UnverifiedEmailException
# from apps.rallz_auth.serializers import (OrganizationSerializer,
#                                          RegisterSerializer,
#                                          UserProfileSerializer, UserSerializer)
from apps.rallz_auth_multitenant.models import (TenantOrganization,
                                                TenantOrganizationOwner,
                                                TenantOrganizationUser,
                                                TenantUser)

# from organizations.utils import create_organization


try:
    from allauth.account.adapter import get_adapter
    from allauth.account.utils import setup_user_email
    from allauth.utils import email_address_exists
except ImportError:
    raise ImportError("allauth needs to be added to INSTALLED_APPS.")

from .models import UserProfile

UserModel = TenantUser


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('bio', 'photo_url')


class UserSerializer(serializers.ModelSerializer):
    """
    User model w/o password
    """
    is_admin = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField(source="get_full_name")
    email_verified = serializers.SerializerMethodField(
        source="get_email_verified")
    enabled = serializers.BooleanField(source="is_active", read_only=True)
    profile = UserProfileSerializer(source="userprofile",
                                    required=False)

    class Meta:
        model = UserModel
        fields = ('id', 'is_admin', 'email_verified', 'enabled', 'first_name', 'last_name', 'full_name',
                  'profile', 'email', 'organization', 'groups', 'user_permissions', 'last_login', 'date_joined')

        read_only_fields = ('email', 'groups', 'last_login', 'full_name',
                            'date_joined', 'user_permissions')

        # dynamic serializer based on fields given to it
    def __init__(self, *args, **kwargs):
        try:
            # Don't pass the 'fields' arg up to the superclass
            fields = kwargs.get('context').pop('fields', None)
            # Instantiate the superclass normally
            super(UserSerializer, self).__init__(*args, **kwargs)

            if fields is not None:
                # Drop any fields that are not specified in the `fields` argument.
                allowed = set(fields)
                existing = set(self.fields)
                for field_name in existing - allowed:
                    self.fields.pop(field_name)
        except AttributeError:
            pass

    def get_is_admin(self, user):
        return user.is_staff or user.is_superuser

    def get_full_name(self, user):
        return user.get_full_name()

    # def get_organization(self, user):
    #     return user.organizations_organization.get()

    def get_email_verified(self, user):
        return user.emailaddress_set.get(user=user, primary=True).verified

    def validate_email(self, email):
        if self.instance and email != self.instance.email:
            raise serializers.ValidationError(
                "email cannot be changed once set")
            # maybe set email here
        return email

    def get_cleaned_data(self):
        return {
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'email': self.validated_data.get('email', ''),
            # 'password1': self.validated_data.get('password1', generate_random_string(64)),
        }

    # def create(self, validated_data):
    #     request = self.context['request']
    #     adapter = get_adapter()
    #     user = adapter.new_user(request)
    #     self.cleaned_data = self.get_cleaned_data()
    #     saved_user = adapter.save_user(request, user, self)
    #     # profile
    #     userprofile = self.validated_data.get('userprofile', {})
    #     profile_serializer = UserProfileSerializer(data=userprofile)
    #     if profile_serializer.is_valid():
    #         profile_serializer.save(user=saved_user)

    #     # organizations

    #     # from allauth.account.utils import setup_user_email
    #     setup_user_email(request, user, [])
    #     return user

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get(
            'first_name', instance.first_name)
        instance.last_name = validated_data.get(
            'last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)

        instance.save()

        # logger.info(msg=**validated_data)
        # print(validated_data)

        profile_data = validated_data.get('userprofile', None)
        if hasattr(instance, 'userprofile'):
            profile_serializer = UserProfileSerializer(
                instance.userprofile, data=profile_data)
            if profile_serializer.is_valid():
                profile_serializer.save()
        else:
            profile_serializer = UserProfileSerializer(data=profile_data)
            if profile_serializer.is_valid():
                profile_serializer.save(user=instance)
        return instance


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def authenticate(self, **kwargs):
        from django.contrib.auth import authenticate

        # Did we get back an active user?
        if self._can_user_authenticate(self.context['request'], **kwargs):
            return authenticate(self.context['request'], **kwargs)
        return None

    def _can_user_authenticate(self, request, username=None,  **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None:
            return False
        try:
            user = UserModel._default_manager.get_by_natural_key(username)
            self.validate_auth_user_status(user)
            return True
        except UserModel.DoesNotExist:
            return False

    def get_auth_user(self,  email, password):
        """
        Retrieve the auth user from given POST payload by using
        either `allauth` auth scheme or bare Django auth scheme.

        Returns the authenticated user instance if credentials are correct,
        else `None` will be returned
        """
        if 'allauth' in settings.INSTALLED_APPS:
            return self.get_auth_user_using_allauth(email, password)
        return self.get_auth_user_using_orm(email, password)

    def get_auth_user_using_allauth(self, email, password):
        # from allauth.account import app_settings
        return self._validate_email(email, password)

    def get_auth_user_using_orm(self, email, password):
        if email:
            try:
                user_email = UserModel.objects.get(
                    email__iexact=email).get_email()
            except UserModel.DoesNotExist:
                pass

        if user_email:
            return self._validate_email(email, password)

        return None

    def _validate_email(self, email, password):
        user = None

        if email and password:
            user = self.authenticate(email=email, password=password)
        else:
            raise exceptions.ValidationError(
                _('Must include "email" and "password".'))
        return user

    def validate_auth_user_status(self, user):
        if not user.is_active:
            raise auth_exceptions.UserDisabledException

    def validate_email_verification_status(self, user):
        from allauth.account import app_settings
        if app_settings.EMAIL_VERIFICATION == app_settings.EmailVerificationMethod.MANDATORY:
            email_address = user.emailaddress_set.get(email=user.email)
            if not email_address.verified:
                raise auth_exceptions.UnverifiedEmailException(
                    {'email': _('E-mail is not verified.')})

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = self.get_auth_user(email, password)

        if not user:
            # authentication failed
            # auth_exceptions.AuthenticationFailed
            raise exceptions.AuthenticationFailed(
                detail=_('Unable to log in with provided credentials.'))

        # If required, is the email verified?
        if 'dj_rest_auth.registration' in settings.INSTALLED_APPS:
            self.validate_email_verification_status(user)

        attrs['user'] = user
        return attrs


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=settings.ACCOUNT_EMAIL_REQUIRED)
    first_name = serializers.CharField(required=True, write_only=True, error_messages={
                                       'required': 'First name is required'})
    last_name = serializers.CharField(required=True, write_only=True, error_messages={
                                      'required': 'Last name is required'})
    password1 = serializers.CharField(
        style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(
        style={'input_type': 'password'}, write_only=True)

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if settings.ACCOUNT_UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise auth_exceptions.EmailExistsException
        return email

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise auth_exceptions.InvalidPasswordException(
                _("The two password fields didn't match."))
        return data

    def custom_signup(self, request, user):
        pass

    def get_cleaned_data(self):
        return {
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', '')
        }

    def save(self, request):
        adapter = get_adapter(request)
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        saved_user = adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])

        # bets to save other local models after setup is done then save
        # mayve add the userprofile serializer to the form and let them add data from there and us that
        UserProfile.objects.create(user=saved_user)
        saved_user.save()
        return saved_user


class TenantUserSerializer(UserSerializer):
    # organization = OrganizationSerializer(required=False, allow_null=True)

    class Meta(UserSerializer.Meta):
        model = UserModel
        fields = UserSerializer.Meta.fields + ('organization',)
        read_only_fields = ('organization',)  # + USER_FIELDS


class RegisterOrganizationSerializer(RegisterSerializer):
    organization = serializers.CharField(required=True, write_only=True, error_messages={
        'required': 'organization is required'})

    # profile = UserProfileSerializer(required=False)

    def get_cleaned_data(self):
        return {
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'organization': self.validated_data.get('organization', '')
        }

    def validate_email(self, email):
        return email

    def save(self, request):
        adapter = get_adapter()
        self.cleaned_data = self.get_cleaned_data()
        email = self.cleaned_data.get('email')
        organization_name = self.cleaned_data.get('organization')
        # profile_data = self.validated_data.get('profile', None)
        user = None
        if email_address_exists(email):
            print('email exists')
            try:
                user = UserModel._default_manager.get_by_natural_key(email)
            except UserModel.DoesNotExist:

                user = adapter.new_user(request)
        else:
            user = adapter.new_user(request)

        from apps.rallz_auth.utils import model_field_names  # create_organization
        from apps.rallz_auth_multitenant.models import (TenantOrganization,
                                                        TenantOrganizationOwner,
                                                        TenantOrganizationUser,
                                                        UserProfile)

        if user is None:
            print('user is None:', user)
            return
        # is_admin = bool(user.is_staff or user.is_superuser)
        org_defaults = {}
        org_user_defaults = {}
        if "is_admin" in model_field_names(TenantOrganizationUser):
            org_user_defaults = {"is_admin": True}
        org_defaults.update({"is_active": True})
        org_defaults.update({"name": organization_name})
        organization = TenantOrganization.objects.create(**org_defaults)
        user.organization = organization
        user.is_staff = True
        user.is_superuser = True
        adapter.save_user(request, user, self)

        org_user_defaults.update({"organization": organization, "user": user})
        new_user = TenantOrganizationUser.objects.create(**org_user_defaults)

        TenantOrganizationOwner.objects.create(
            organization=organization, organization_user=new_user
        )

        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user


class OrganizationUserSerializer(serializers.ModelSerializer):
    is_admin = serializers.SerializerMethodField()

    class Meta:
        # depth = 1
        model = TenantOrganizationUser
        fields = ['id', 'name', 'user', 'is_admin',
                  'created_at', 'updated_at']

    def get_is_admin(self, value):
        return value.organization.is_admin(value.user)
        # return False


class OrganizationOwnerSerializer(OrganizationUserSerializer):
    name = serializers.CharField(source='organization_user.name')

    class Meta(OrganizationUserSerializer.Meta):
        fields_base = OrganizationUserSerializer.Meta.fields
        fields = fields_base


class OrganizationSerializerWithUsers(serializers.ModelSerializer):

    users = OrganizationUserSerializer(source="organization_users", many=True)

    class Meta:
        # depth = 1
        model = TenantOrganization
        fields = ('id', 'slug', 'name', 'is_active', 'users',
                  'created_at', 'updated_at')
