# # Create your models here.
# from django.contrib.auth import get_user_model
# from django.utils.translation import gettext_lazy as _
# from django_multitenant.mixins import TenantManagerMixin, TenantModelMixin
# from django_multitenant.models import TenantModel

# from apps.rallz_auth.models import UserManager


# class TenantUserManager(TenantManagerMixin, UserManager):
#     pass


# class TenantUser(TenantModelMixin, get_user_model()):

#     tenant_id = 'user_id'

#     objects = TenantUserManager()

#     class Meta():
#         ordering = ('first_name',)
#         verbose_name = _("tenant user")
#         verbose_name_plural = _("tenant users")


# # class TenantOrganization(TenantModel, Organization):
# #     tenant_id = 'id'
