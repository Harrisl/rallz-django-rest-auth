from django.urls import path, include
from apps.rallz_auth.urls import auth_urlpatterns, accounts_urlpatterns


urlpatterns_v1 = [
    path('', include('drf_problems.urls')),
    # https://djoser.readthedocs.io/en/latest/getting_started.html#available-endpoints
    path('auth/', include(auth_urlpatterns)),
    path('accounts/', include(accounts_urlpatterns)),
]
