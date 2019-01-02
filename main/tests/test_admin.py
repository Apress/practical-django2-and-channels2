from datetime import datetime
from decimal import Decimal
from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from main import factories
from main import models
import re


def compare_bodies(content, expected_content):
    c_match = re.search(r'<body>(.*)</body>', content, re.DOTALL|re.M)
    e_match = re.search(r'<body>(.*)</body>', expected_content, re.DOTALL|re.M)
    if c_match and e_match:
        return c_match.group(1) == e_match.group(1)
    return False


class TestAdminViews(TestCase):
    def test_most_bought_products(self):
        products = [
            factories.ProductFactory(name="A", active=True),
            factories.ProductFactory(name="B", active=True),
            factories.ProductFactory(name="C", active=True),
        ]
        orders = factories.OrderFactory.create_batch(3)
        factories.OrderLineFactory.create_batch(
            2, order=orders[0], product=products[0]
        )
        factories.OrderLineFactory.create_batch(
            2, order=orders[0], product=products[1]
        )
        factories.OrderLineFactory.create_batch(
            2, order=orders[1], product=products[0]
        )
        factories.OrderLineFactory.create_batch(
            2, order=orders[1], product=products[2]
        )
        factories.OrderLineFactory.create_batch(
            2, order=orders[2], product=products[0]
        )
        factories.OrderLineFactory.create_batch(
            1, order=orders[2], product=products[1]
        )

        user = models.User.objects.create_superuser(
            "user2", "pw432joij"
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("admin:most_bought_products"),
            {"period": "90"},
        )
        self.assertEqual(response.status_code, 200)

        data = dict(
            zip(
                response.context["labels"],
                response.context["values"],
            )
        )

        self.assertEqual(data, {"B": 3, "C": 2, "A": 6})

    def test_invoice_renders_exactly_as_expected(self):
        products = [
            factories.ProductFactory(
                name="A", active=True, price=Decimal("10.00")
            ),
            factories.ProductFactory(
                name="B", active=True, price=Decimal("12.00")
            ),
        ]

        with patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = datetime(
                2018, 7, 25, 12, 00, 00
            )
            order = factories.OrderFactory(
                id=12,
                billing_name="John Smith",
                billing_address1="add1",
                billing_address2="add2",
                billing_zip_code="zip",
                billing_city="London",
                billing_country="UK",
            )

        factories.OrderLineFactory.create_batch(
            2, order=order, product=products[0]
        )
        factories.OrderLineFactory.create_batch(
            2, order=order, product=products[1]
        )

        user = models.User.objects.create_superuser(
            "user2", "pw432joij"
        )
        self.client.force_login(user)

        response = self.client.get(
            reverse(
                "admin:invoice", kwargs={"order_id": order.id}
            )
        )
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf8")

        with open(
            "main/fixtures/invoice_test_order.html", "r"
        ) as fixture:
            expected_content = fixture.read()
        self.assertTrue(compare_bodies(content, expected_content))

        response = self.client.get(
            reverse(
                "admin:invoice", kwargs={"order_id": order.id}
            ),
            {"format": "pdf"},
        )
        self.assertEqual(response.status_code, 200)
        content = response.content

        with open(
            "main/fixtures/invoice_test_order.pdf", "rb"
        ) as fixture:
            expected_content = fixture.read()

        self.assertEqual(content[:5], expected_content[:5])
