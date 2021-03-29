from django.urls import path, re_path, include
from rest_framework_simplejwt.views import TokenVerifyView

from dj_rest_auth.jwt_auth import get_refresh_view
from dj_rest_auth.views import (LoginView, LogoutView, PasswordChangeView,
                                PasswordResetConfirmView, PasswordResetView,
                                UserDetailsView)

from dj_rest_auth.registration.views import RegisterView, VerifyEmailView
from allauth.account.views import confirm_email

from apps.rallz_auth.views import complete_view, null_view, RegisterOrganizationView


urlpatterns = [
    # URLs that do not require a session or valid token
    path('password/reset/', PasswordResetView.as_view(),
         name='rest_password_reset'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(),
         name='rest_password_reset_confirm'),
    path('signin/', LoginView.as_view(), name='rest_signin'),
    # URLs that require a user to be logged in with a valid session / token.
    path('signout/', LogoutView.as_view(), name='rest_signout'),
    path('me/', UserDetailsView.as_view(), name='rest_user_details'),
    path('password/change/', PasswordChangeView.as_view(),
         name='rest_password_change')
]

# registration
urlpatterns += [
    path('signup/organization/', RegisterOrganizationView.as_view(),
         name='rest_organization_signup'),
    path('signup/', RegisterView.as_view(), name='rest_signup'),

    path('signup/complete/', complete_view,
         name='account-registration-confirm-complete'),

    path('signup/account-email-verification-sent/', null_view,
         name='account_email_verification_sent'),
    # django-allauth https://github.com/pennersr/django-allauth/blob/master/allauth/account/views.py
    re_path(r'^confirm-email/(?P<key>[-:\w]+)/$', confirm_email,
            name='account_confirm_email'),
    path('verify-email/', VerifyEmailView.as_view(), name='rest_verify_email'),
]

urlpatterns += [
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('token/refresh/', get_refresh_view().as_view(), name='token_refresh'),
]
