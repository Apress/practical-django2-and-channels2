from decimal import Decimal
from django.test import TestCase
from main import models
from main import factories


class TestModel(TestCase):
    def test_active_manager_works(self):
        factories.ProductFactory.create_batch(2, active=True)
        factories.ProductFactory(active=False)
        self.assertEqual(len(models.Product.objects.active()), 2)

    def test_create_order_works(self):
        p1 = factories.ProductFactory()
        p2 = factories.ProductFactory()
        user1 = factories.UserFactory()
        billing = factories.AddressFactory(user=user1)
        shipping = factories.AddressFactory(user=user1)

        basket = models.Basket.objects.create(user=user1)
        models.BasketLine.objects.create(
            basket=basket, product=p1
        )
        models.BasketLine.objects.create(
            basket=basket, product=p2
        )

        with self.assertLogs("main.models", level="INFO") as cm:
            order = basket.create_order(billing, shipping)

        self.assertGreaterEqual(len(cm.output), 1)

        order.refresh_from_db()

        self.assertEquals(order.user, user1)
        self.assertEquals(
            order.billing_address1, billing.address1
        )
        self.assertEquals(
            order.shipping_address1, shipping.address1
        )

        self.assertEquals(order.lines.all().count(), 2)
        lines = order.lines.all()
        self.assertEquals(lines[0].product, p1)
        self.assertEquals(lines[1].product, p2)
