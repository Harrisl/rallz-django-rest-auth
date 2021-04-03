from django.urls import path, re_path

from .views import TenantOrganizationViewSet, OrganizationRegisterView, OrganizationUserDetailsView, null_view, complete_view
from dj_rest_auth.registration.views import VerifyEmailView, LoginView
from allauth.account.views import confirm_email


# TenantOrganizationViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'organizations', TenantOrganizationViewSet,
                basename='organizations')

auth_urlpatterns = [
    # django-allauth https://github.com/pennersr/django-allauth/blob/master/allauth/account/views.py

    re_path(r'^confirm-email/(?P<key>[-:\w]+)/$',
            confirm_email, name='account_confirm_email'),
    path('verify-email/', VerifyEmailView.as_view(), name='rest_verify_email'),
]
multitenant_auth_urlpatterns = [
    path('me/', OrganizationUserDetailsView.as_view(), name='rest_user_details'),
    path('signin/', LoginView.as_view(), name='rest_signin'),
    path('signup/account-email-verification-sent/', null_view,
         name='account_email_verification_sent'),
    path('signup/complete/', complete_view,
         name='account-registration-confirm-complete'),
    path('signup/organization/', OrganizationRegisterView.as_view(),
         name='rest_organization_signup'),


]
multitenant_auth_urlpatterns += auth_urlpatterns
organization_urls = router.urls
