from django.urls import path, include
from apps.rallz_auth import urls as auth_urls


urlpatterns_v1 = [
    path('', include('drf_problems.urls')),
    # https://djoser.readthedocs.io/en/latest/getting_started.html#available-endpoints
    path('auth/', include(auth_urls)),
]
