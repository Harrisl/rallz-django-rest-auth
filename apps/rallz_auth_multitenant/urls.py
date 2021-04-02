from django.urls import path

from .views import OrganizationRegisterView, OrganizationUserDetailsView

multitenant_auth_urlpatterns = [
    path('me/', OrganizationUserDetailsView.as_view(), name='rest_user_details'),
    path('signup/organization/', OrganizationRegisterView.as_view(),
         name='rest_organization_signup')
]
