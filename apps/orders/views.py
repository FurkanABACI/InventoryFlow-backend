from apps.core.views import BaseModelViewSet
from apps.orders.models import Order
from apps.orders.serializers import OrderSerializer


class OrderViewSet(BaseModelViewSet):
    queryset = Order.objects.prefetch_related("items__product").all()
    serializer_class = OrderSerializer
