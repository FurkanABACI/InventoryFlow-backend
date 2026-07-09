from apps.core.views import BaseModelViewSet
from apps.receiving.models import GoodsReceipt
from apps.receiving.serializers import GoodsReceiptSerializer


class GoodsReceiptViewSet(BaseModelViewSet):
    queryset = GoodsReceipt.objects.select_related("supplier").prefetch_related(
        "items__product",
    )
    serializer_class = GoodsReceiptSerializer
