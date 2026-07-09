from core.views import BaseModelViewSet
from core.permissions import IsInventoryManager
from orders.models import Order
from orders.serializers import OrderSerializer


class OrderViewSet(BaseModelViewSet):
    queryset = Order.objects.prefetch_related("items__product").all()
    serializer_class = OrderSerializer
    permission_classes = (IsInventoryManager,)
