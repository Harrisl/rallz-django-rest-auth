# from django.contrib import admin
# # from django.contrib.auth import get_user_model
# from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
# from django.utils.translation import ugettext_lazy as _

# from .models import TenantUser

# # Register your models here.


# @admin.register(TenantUser)
# class TenantUserAdmin(DjangoUserAdmin):
#     """Define admin model for custom User model with no email field."""

#     fieldsets = (
#         (None, {'fields': ('email', 'password')}),
#         (_('Personal info'), {'fields': ('first_name', 'last_name')}),
#         (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
#                                        'groups', 'user_permissions')}),
#         (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
#         (_('Organization data'), {'fields': ('organizations',)}),
#     )
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('email', 'password1', 'password2'),
#         }),
#     )
#     list_display = ('email', 'first_name', 'last_name',
#                     'is_active', 'is_staff')
#     search_fields = ('email', 'first_name', 'last_name')
#     ordering = ('email',)