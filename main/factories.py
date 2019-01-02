import factory
import factory.fuzzy
from . import models


class UserFactory(factory.django.DjangoModelFactory):
    email = "user@site.com"

    class Meta:
        model = models.User
        django_get_or_create = ("email",)


class ProductFactory(factory.django.DjangoModelFactory):
    price = factory.fuzzy.FuzzyDecimal(1.0, 1000.0, 2)

    class Meta:
        model = models.Product


class AddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Address


class OrderLineFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.OrderLine


class OrderFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = models.Order
