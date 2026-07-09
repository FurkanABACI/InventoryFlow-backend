from django.db import transaction
from rest_framework import serializers

from apps.catalog.models import Product
from apps.core.serializers import BaseModelSerializer
from apps.orders.models import Order, OrderItem


class OrderItemReadSerializer(BaseModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta(BaseModelSerializer.Meta):
        model = OrderItem
        fields = BaseModelSerializer.Meta.fields + (
            "product",
            "product_name",
            "quantity",
            "unit_price",
        )


class OrderItemWriteSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.filter(is_active=True))
    quantity = serializers.IntegerField(min_value=1)


class OrderSerializer(BaseModelSerializer):
    items = OrderItemReadSerializer(many=True, read_only=True)
    order_items = OrderItemWriteSerializer(many=True, write_only=True)

    class Meta(BaseModelSerializer.Meta):
        model = Order
        fields = BaseModelSerializer.Meta.fields + (
            "customer_name",
            "note",
            "items",
            "order_items",
        )

    def validate_order_items(self, value):
        if not value:
            raise serializers.ValidationError("Siparis icin en az bir urun secilmelidir.")

        return value

    def validate(self, attrs):
        order_items = attrs.get("order_items", [])

        for item in order_items:
            product = item["product"]
            quantity = item["quantity"]

            if product.stock < quantity:
                raise serializers.ValidationError({
                    "order_items": f"{product.name} icin yeterli stok yok. Mevcut stok: {product.stock}."
                })

        return attrs

    def create(self, validated_data):
        order_items = validated_data.pop("order_items")

        with transaction.atomic():
            order = Order.objects.create(**validated_data)

            for item in order_items:
                product = Product.objects.select_for_update().get(id=item["product"].id)
                quantity = item["quantity"]

                if product.stock < quantity:
                    raise serializers.ValidationError({
                        "order_items": f"{product.name} icin yeterli stok yok. Mevcut stok: {product.stock}."
                    })

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=product.price,
                )

                product.stock -= quantity
                product.save(update_fields=["stock", "updated_at"])

        return order
