from allauth.account.views import confirm_email
from dj_rest_auth.registration.views import RegisterView, VerifyEmailView
from dj_rest_auth.views import (LoginView, LogoutView, PasswordChangeView,
                                PasswordResetConfirmView, PasswordResetView,
                                UserDetailsView)
from django.urls import path, re_path

from .views import complete_view, null_view, OrganizationViewSet

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet,
                basename='organizations')

auth_urlpatterns = [
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
auth_urlpatterns += [

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

auth_urlpatterns += [
    # path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # path('token/refresh/', get_refresh_view().as_view(), name='token_refresh'),
]

accounts_urlpatterns = [
    #     path('organizations/', OrganizationViewSet.as_view(), name='organizations')
    # path('organizations/', include(OrganizationViewSet))
]
accounts_urlpatterns += router.urls
