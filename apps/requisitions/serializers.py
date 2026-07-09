from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.catalog.models import Product
from apps.core.serializers import BaseModelSerializer
from apps.requisitions.models import StockRequest, StockRequestItem


class StockRequestItemReadSerializer(BaseModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    sku = serializers.CharField(source="product.sku", read_only=True)
    current_stock = serializers.IntegerField(source="product.stock", read_only=True)

    class Meta(BaseModelSerializer.Meta):
        model = StockRequestItem
        fields = BaseModelSerializer.Meta.fields + (
            "product",
            "product_name",
            "sku",
            "current_stock",
            "quantity",
            "delivered_quantity",
        )


class StockRequestItemWriteSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True)
    )
    quantity = serializers.IntegerField(min_value=1)


class StockRequestSerializer(BaseModelSerializer):
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    items = StockRequestItemReadSerializer(many=True, read_only=True)
    request_items = StockRequestItemWriteSerializer(many=True, write_only=True)
    total_quantity = serializers.SerializerMethodField()
    can_fulfill = serializers.SerializerMethodField()

    class Meta(BaseModelSerializer.Meta):
        model = StockRequest
        fields = BaseModelSerializer.Meta.fields + (
            "department",
            "requester_name",
            "note",
            "status",
            "status_label",
            "fulfilled_at",
            "items",
            "request_items",
            "total_quantity",
            "can_fulfill",
        )
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + (
            "fulfilled_at",
        )

    def get_total_quantity(self, obj):
        return sum(item.quantity for item in obj.items.all())

    def get_can_fulfill(self, obj):
        if obj.status != StockRequest.Status.PENDING:
            return False

        return all(item.product.stock >= item.quantity for item in obj.items.all())

    def validate_request_items(self, value):
        if not value:
            raise serializers.ValidationError("Talep icin en az bir urun secilmelidir.")

        return value

    def create(self, validated_data):
        request_items = validated_data.pop("request_items")

        with transaction.atomic():
            stock_request = StockRequest.objects.create(**validated_data)

            for item in request_items:
                StockRequestItem.objects.create(
                    request=stock_request,
                    product=item["product"],
                    quantity=item["quantity"],
                )

        return stock_request


class StockRequestFulfillmentSerializer(serializers.Serializer):
    detail = serializers.CharField(read_only=True)

