from apps.core.views import BaseModelViewSet
from apps.stock.models import StockMovement
from apps.stock.serializers import StockMovementSerializer


class StockMovementViewSet(BaseModelViewSet):
    queryset = StockMovement.objects.select_related("product").all()
    serializer_class = StockMovementSerializer

