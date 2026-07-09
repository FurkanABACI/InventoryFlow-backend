from core.permissions import IsInventoryManager
from core.views import BaseModelViewSet
from stock.models import StockMovement
from stock.serializers import StockMovementSerializer


class StockMovementViewSet(BaseModelViewSet):
    queryset = StockMovement.objects.select_related("product").all()
    serializer_class = StockMovementSerializer
    permission_classes = (IsInventoryManager,)
