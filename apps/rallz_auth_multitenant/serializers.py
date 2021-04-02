# import logging

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.rallz_auth.serializers import (OrganizationSerializer,
                                         RegisterSerializer,
                                         UserProfileSerializer, UserSerializer)

# from organizations.utils import create_organization


# from .. import exceptions as auth_exceptions  # UnverifiedEmailException
try:
    from allauth.account.adapter import get_adapter
    from allauth.account.utils import setup_user_email
    from allauth.utils import email_address_exists
except ImportError:
    raise ImportError("allauth needs to be added to INSTALLED_APPS.")


UserModel = get_user_model()


class TenantUserSerializer(UserSerializer):
    organization = OrganizationSerializer(required=False, allow_null=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('organization',)
        read_only_fields = ('organization',)  # + USER_FIELDS


class RegisterOrganizationSerializer(RegisterSerializer):
    organization = serializers.CharField(required=True, write_only=True, error_messages={
        'required': 'organization is required'})

    profile = UserProfileSerializer(required=False)

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
        if email and email_address_exists(email):
            try:
                user = UserModel._default_manager.get_by_natural_key(email)

                # profile_serializer = UserProfileSerializer(
                #     user.userprofile, data=profile_data)
                # if profile_serializer.is_valid():
                #     profile_serializer.save()

            except UserModel.DoesNotExist:
                user = adapter.new_user(request)
                user = adapter.save_user(request, user, self)
                # profile_serializer = UserProfileSerializer(data=profile_data)

                # if profile_serializer.is_valid():
                #     profile_serializer.save(user=saved_user)
        else:
            user = adapter.new_user(request)
            user = adapter.save_user(request, user, self)
            # if profile_data is not None:
            #     profile_serializer = UserProfileSerializer(data=profile_data)
            #     if profile_serializer.is_valid():
            #         profile_serializer.save(user=saved_user)

            setup_user_email(request, user, [])
        from apps.rallz_auth.utils import create_organization
        create_organization(user, organization_name, is_active=True,
                            org_user_defaults={'is_admin': user.is_staff or user.is_superuser})
        user.save()

        return user
