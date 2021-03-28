from django.urls import re_path

from rest_framework_simplejwt import views as jwt_views

from dj_rest_auth.views import LoginView

urlpatterns = [
    re_path(r'^token/pair/$', jwt_views.token_obtain_pair,
            name='token_obtain_pair'),
    re_path(r'^token/refresh/$', jwt_views.token_refresh, name='token_refresh'),

    re_path(r'^token/sliding/$', jwt_views.token_obtain_sliding,
            name='token_obtain_sliding'),
    re_path(r'^token/sliding/refresh/$',
            jwt_views.token_refresh_sliding, name='token_refresh_sliding'),

    re_path(r'^token/verify/$', jwt_views.token_verify, name='token_verify'),

    # test
    re_path(r'^signin/$', LoginView.as_view(), name='rest_signin'),

    # re_path(r'^test-view/$', views.test_view, name='test_view'),
]
