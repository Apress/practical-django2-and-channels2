from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from main import factories
from main import models


class TestEndpoints(APITestCase):
    def test_mobile_flow(self):
        user = factories.UserFactory(email="mobileuser@site.com")
        token = Token.objects.get(user=user)
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + token.key
        )

        orders = factories.OrderFactory.create_batch(
            2, user=user
        )
        a = factories.ProductFactory(
            name="The book of A", active=True, price=12.00
        )
        b = factories.ProductFactory(
            name="The B Book", active=True, price=14.00
        )
        factories.OrderLineFactory.create_batch(
            2, order=orders[0], product=a
        )
        factories.OrderLineFactory.create_batch(
            2, order=orders[1], product=b
        )

        response = self.client.get(reverse("mobile_my_orders"))
        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )

        expected = [
            {
                "id": orders[1].id,
                "image": None,
                "price": 28.0,
                "summary": "2 x The B Book",
            },
            {
                "id": orders[0].id,
                "image": None,
                "price": 24.0,
                "summary": "2 x The book of A",
            },
        ]
        self.assertEqual(response.json(), expected)

    def test_mobile_login_works(self):
        user = models.User.objects.create_user(
            "user1", "abcabcabc"
        )
        response = self.client.post(
            reverse("mobile_token"),
            {"username": "user1", "password": "abcabcabc"},
        )
        jsonresp = response.json()
        self.assertIn("token", jsonresp)
