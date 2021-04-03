# from django_multitenant.utils import set_current_tenant

from apps.rallz_auth.managers import UserManager
from apps.rallz_auth.utils import create_organization

# from .models import TenantOrganizationUser, TenantOrganization, TenantOrganizationOwner
# from functools import partial
# create_org = partial(create_organization,
#                     user_model=TenantOrganizationUser, owner_model=TenantOrganizationOwner,
#                     model=TenantOrganization)


class TenantUserManager(UserManager):
    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser and Organization with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        user = self._create_user(email, password, **extra_fields)
        # user = super().create_superuser(email, password, **extra_fields)
        user.emailaddress_set.create(email=email, verified=True, primary=True)
        org_name = "{0}-organization".format(user.get_full_name())
        create_organization(user, org_name, is_active=user.is_active,
                            org_user_defaults={
                                'is_admin': user.is_staff or user.is_superuser}, use_tenant=True)
        # user.save()
        return user

    # def create_organization_and_set_tenant(self, user, name):
    #     org_tenant = default_org_model().objects.create({"is_active": user.is_active, name: name})
    #     # s=Store.objects.all()[0]
    #     set_current_tenant(org_tenant)
    #     pass
