from rest_framework import serializers, viewsets
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import models


class OrderLineSerializer(
    serializers.HyperlinkedModelSerializer
):
    product = serializers.StringRelatedField()

    class Meta:
        model = models.OrderLine
        fields = ("id", "order", "product", "status")
        read_only_fields = ("id", "order", "product")


class PaidOrderLineViewSet(viewsets.ModelViewSet):
    queryset = models.OrderLine.objects.filter(
        order__status=models.Order.PAID
    ).order_by("-order__date_added")
    serializer_class = OrderLineSerializer
    filter_fields = ("order", "status")


class OrderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Order
        fields = (
            "shipping_name",
            "shipping_address1",
            "shipping_address2",
            "shipping_zip_code",
            "shipping_city",
            "shipping_country",
            "date_updated",
            "date_added",
        )


class PaidOrderViewSet(viewsets.ModelViewSet):
    queryset = models.Order.objects.filter(
        status=models.Order.PAID
    ).order_by("-date_added")
    serializer_class = OrderSerializer


@api_view()
@permission_classes((IsAuthenticated,))
def my_orders(request):
    user = request.user
    orders = models.Order.objects.filter(user=user).order_by(
        "-date_added"
    )
    data = []
    for order in orders:
        data.append(
            {
                "id": order.id,
                "image": order.mobile_thumb_url,
                "summary": order.summary,
                "price": order.total_price,
            }
        )
    return Response(data)
