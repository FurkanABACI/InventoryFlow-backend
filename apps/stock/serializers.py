from rest_framework import serializers

from apps.core.serializers import BaseModelSerializer
from apps.stock.models import StockMovement


class StockMovementSerializer(BaseModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    sku = serializers.CharField(source="product.sku", read_only=True)
    movement_type_label = serializers.CharField(
        source="get_movement_type_display",
        read_only=True,
    )

    class Meta(BaseModelSerializer.Meta):
        model = StockMovement
        fields = BaseModelSerializer.Meta.fields + (
            "product",
            "product_name",
            "sku",
            "movement_type",
            "movement_type_label",
            "quantity",
            "unit_cost",
            "source_type",
            "source_id",
            "note",
        )

