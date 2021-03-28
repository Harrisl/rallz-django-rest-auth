"""Integrate with admin module."""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import User, UserProfile


def get_user_search_fields():
    user = get_user_model()
    return filter(
        lambda a: a and hasattr(user, a),
        [
            "first_name",
            "last_name",
            "email",
        ],
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "bio", "photo_url")
    list_filter = ("bio", "photo_url")
    search_fields = []
    raw_id_fields = ("user",)

    search_fields = ('email', 'bio', 'photo_url')


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
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


# try:
#     from allauth.account.models import EmailAddress

#     @admin.register(EmailAddress)
#     class EmailAddressAdmin(admin.ModelAdmin):
#         list_display = ("email", "user", "primary", "verified")
#         list_filter = ("primary", "verified")
#         search_fields = []
#         raw_id_fields = ("user",)

#         def get_search_fields(self, request):
#             base_fields = get_user_search_fields()
#             return ["email"] + list(map(lambda a: "user__" + a, base_fields))

# except ImportError:
#     pass
