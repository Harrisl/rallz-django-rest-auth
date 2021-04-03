from django.urls import include, path

# from apps.rallz_auth.urls import accounts_urlpatterns, auth_urlpatterns
from apps.rallz_auth_multitenant.urls import multitenant_auth_urlpatterns, organization_urls

urlpatterns_v1 = [
    # path('', include('drf_problems.urls')),
    # https://djoser.readthedocs.io/en/latest/getting_started.html#available-endpoints
    path('', include(organization_urls)),
    path('auth/', include(multitenant_auth_urlpatterns)),
    # path('auth/', include(auth_urlpatterns)),
    # path('accounts/', include(accounts_urlpatterns)),
]
