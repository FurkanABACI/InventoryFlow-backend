from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from catalog.models import Product
from core.serializers import BaseModelSerializer
from requisitions.choices import StockRequestStatus
from requisitions.models import StockRequest, StockRequestItem


class StockRequestItemReadSerializer(BaseModelSerializer):
    product_name = serializers.SerializerMethodField()
    sku = serializers.SerializerMethodField()
    current_stock = serializers.SerializerMethodField()
    has_product_card = serializers.SerializerMethodField()

    class Meta(BaseModelSerializer.Meta):
        model = StockRequestItem
        fields = BaseModelSerializer.Meta.fields + (
            "product",
            "product_name",
            "sku",
            "current_stock",
            "has_product_card",
            "requested_product_name",
            "requested_product_note",
            "quantity",
            "delivered_quantity",
        )

    def get_product_name(self, obj):
        if obj.product:
            return obj.product.name

        return obj.requested_product_name

    def get_sku(self, obj):
        if obj.product:
            return obj.product.sku

        return "Ürün kartı yok"

    def get_current_stock(self, obj):
        if obj.product:
            return obj.product.stock

        return None

    def get_has_product_card(self, obj):
        return bool(obj.product_id)


class StockRequestItemWriteSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    requested_product_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
    )
    requested_product_note = serializers.CharField(required=False, allow_blank=True)
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        product = attrs.get("product")
        requested_product_name = attrs.get("requested_product_name", "").strip()

        if not product and not requested_product_name:
            raise serializers.ValidationError(
                "Urun secilmeli veya listede olmayan urun adi yazilmalidir."
            )

        attrs["requested_product_name"] = requested_product_name
        attrs["requested_product_note"] = attrs.get("requested_product_note", "").strip()
        return attrs


class StockRequestSerializer(BaseModelSerializer):
    requester_username = serializers.CharField(
        source="requester_user.username",
        read_only=True,
    )
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    items = StockRequestItemReadSerializer(many=True, read_only=True)
    request_items = StockRequestItemWriteSerializer(many=True, write_only=True)
    total_quantity = serializers.SerializerMethodField()
    can_fulfill = serializers.SerializerMethodField()

    class Meta(BaseModelSerializer.Meta):
        model = StockRequest
        fields = BaseModelSerializer.Meta.fields + (
            "requester_user",
            "requester_username",
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
            "requester_user",
            "fulfilled_at",
        )

    def get_total_quantity(self, obj):
        return sum(item.quantity for item in obj.items.all())

    def get_can_fulfill(self, obj):
        fulfillable_statuses = [
            StockRequestStatus.PENDING,
            StockRequestStatus.PURCHASE_NEEDED,
        ]

        if obj.status not in fulfillable_statuses:
            return False

        return all(
            item.product and item.product.stock >= item.quantity
            for item in obj.items.all()
        )

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
                    product=item.get("product"),
                    requested_product_name=item.get("requested_product_name", ""),
                    requested_product_note=item.get("requested_product_note", ""),
                    quantity=item["quantity"],
                )

        return stock_request


class StockRequestFulfillmentSerializer(serializers.Serializer):
    detail = serializers.CharField(read_only=True)
