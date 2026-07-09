from django.db import transaction
from rest_framework import serializers

from catalog.models import Product, ProductSupplier, Supplier
from core.serializers import BaseModelSerializer
from receiving.models import GoodsReceipt, GoodsReceiptItem
from stock.models import StockMovement


class GoodsReceiptItemReadSerializer(BaseModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    sku = serializers.CharField(source="product.sku", read_only=True)

    class Meta(BaseModelSerializer.Meta):
        model = GoodsReceiptItem
        fields = BaseModelSerializer.Meta.fields + (
            "product",
            "product_name",
            "sku",
            "quantity",
            "unit_cost",
        )


class GoodsReceiptItemWriteSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.select_related("supplier").filter(is_active=True)
    )
    quantity = serializers.IntegerField(min_value=1)
    unit_cost = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)


class GoodsReceiptSerializer(BaseModelSerializer):
    supplier = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.filter(is_active=True)
    )
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    items = GoodsReceiptItemReadSerializer(many=True, read_only=True)
    receipt_items = GoodsReceiptItemWriteSerializer(many=True, write_only=True)

    class Meta(BaseModelSerializer.Meta):
        model = GoodsReceipt
        fields = BaseModelSerializer.Meta.fields + (
            "supplier",
            "supplier_name",
            "document_no",
            "note",
            "received_at",
            "items",
            "receipt_items",
        )
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + (
            "received_at",
        )

    def validate_receipt_items(self, value):
        if not value:
            raise serializers.ValidationError("Mal kabul icin en az bir urun secilmelidir.")

        return value

    def validate(self, attrs):
        supplier = attrs.get("supplier")

        if supplier and not supplier.is_active:
            raise serializers.ValidationError(
                {"supplier": "Pasif tedarikci ile mal kabul yapilamaz."}
            )

        return attrs

    def create(self, validated_data):
        receipt_items = validated_data.pop("receipt_items")

        with transaction.atomic():
            receipt = GoodsReceipt.objects.create(**validated_data)

            for item in receipt_items:
                product = Product.objects.select_for_update().get(id=item["product"].id)
                quantity = item["quantity"]

                GoodsReceiptItem.objects.create(
                    receipt=receipt,
                    product=product,
                    quantity=quantity,
                    unit_cost=item["unit_cost"],
                )

                ProductSupplier.objects.update_or_create(
                    product=product,
                    supplier=receipt.supplier,
                    defaults={
                        "unit_cost": item["unit_cost"],
                        "is_active": True,
                        "is_preferred": product.supplier_id == receipt.supplier_id,
                    },
                )

                product.stock += quantity
                product.save(update_fields=["stock", "updated_at"])

                StockMovement.objects.create(
                    product=product,
                    movement_type=StockMovement.MovementType.IN,
                    quantity=quantity,
                    unit_cost=item["unit_cost"],
                    source_type="goods_receipt",
                    source_id=receipt.id,
                    note=f"{receipt.supplier.name} mal kabul kaydi",
                )

        return receipt
