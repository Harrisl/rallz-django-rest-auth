from django.contrib import admin
# # from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import (TenantOrganization, TenantOrganizationOwner,
                     TenantOrganizationUser, TenantUser)

# # # Register your models here.


@admin.register(TenantUser)
class TenantUserAdmin(DjangoUserAdmin):
    """Define admin model for custom Tenant User model with no email field."""

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Organization data'), {'fields': ('organization',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name',
                    'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)


# base

class BaseOwnerInline(admin.StackedInline):
    raw_id_fields = ("organization_user",)


class BaseOrganizationAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]
    list_filter = ("is_active",)


class BaseOrganizationUserAdmin(admin.ModelAdmin):
    list_display = ["user", "organization", "is_admin"]
    raw_id_fields = ("user", "organization")


class BaseOrganizationOwnerAdmin(admin.ModelAdmin):
    raw_id_fields = ("organization_user", "organization")


class OwnerInline(BaseOwnerInline):
    model = TenantOrganizationOwner


class OrganizationAdmin(BaseOrganizationAdmin):
    inlines = [OwnerInline]


class OrganizationUserAdmin(BaseOrganizationUserAdmin):
    pass


class OrganizationOwnerAdmin(BaseOrganizationOwnerAdmin):
    pass


admin.site.register(TenantOrganization, OrganizationAdmin)
admin.site.register(TenantOrganizationUser, OrganizationUserAdmin)
admin.site.register(TenantOrganizationOwner, OrganizationOwnerAdmin)
