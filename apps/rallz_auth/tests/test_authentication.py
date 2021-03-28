from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework.test import APIClient, URLPatternsTestCase


from rest_framework_simplejwt import serializers
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import (
    AccessToken, RefreshToken, SlidingToken,
)
from rest_framework_simplejwt.utils import (
    aware_utcnow, datetime_from_epoch, datetime_to_epoch,
)

from .utils import APIViewTestCase, override_api_settings
from .urls import urlpatterns
User = get_user_model()


class TestTokenObtainPairView(APIViewTestCase, URLPatternsTestCase):
    view_name = 'token_obtain_pair'

    urlpatterns = urlpatterns

    login_data = {
        "email": "lharris@altoleap.com",
        "password": "test_password"
    }

    def setUp(self):
        self.email = 'lharris@altoleap.com'
        self.password = 'test_password'

        self.user = User.objects.create_user(
            email=self.email,
            password=self.password,
        )
        self.user.emailaddress_set.create(email=self.user.email)

    def test_user_inactive(self):
        self.user.is_active = False
        self.user.save()

        res = self.view_post(data={
            User.USERNAME_FIELD: self.email,
            'password': self.password,
        })
        self.assertEqual(res.status_code, 401)
        self.assertIn('detail', res.data)

    def test_signin(self):
        self.view_name = 'rest_signin'
        self.user.is_active = True
        self.user.save()
        # signin the new user
        # response = self.client.post(
        #     self.register_url, self.user_data, format="json")
        res = self.view_post(data={
            "email": self.email,
            "password": self.password,
        })
        self.assertEqual(res.status_code, 200)
        # self.assertIn('detail', res.data)
