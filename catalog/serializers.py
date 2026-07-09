from rest_framework import serializers

from catalog.models import Category, Product, ProductSupplier, Supplier
from core.serializers import BaseModelSerializer


class CategorySerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Category
        fields = BaseModelSerializer.Meta.fields + (
            "name",
            "description",
        )


class SupplierSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Supplier
        fields = BaseModelSerializer.Meta.fields + (
            "name",
            "sector",
            "email",
            "phone",
            "address",
            "note",
        )


class ProductSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "sku",
            "stock",
        )


class CategoryWithProductsSerializer(CategorySerializer):
    products = ProductSummarySerializer(many=True, read_only=True)

    class Meta(CategorySerializer.Meta):
        fields = CategorySerializer.Meta.fields + (
            "products",
        )


class ProductSupplierSerializer(BaseModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)

    class Meta(BaseModelSerializer.Meta):
        model = ProductSupplier
        fields = BaseModelSerializer.Meta.fields + (
            "product",
            "product_name",
            "supplier",
            "supplier_name",
            "unit_cost",
            "is_preferred",
        )


class ProductSerializer(BaseModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    supplier_links = ProductSupplierSerializer(many=True, read_only=True)
    supplier_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Supplier.objects.filter(is_active=True),
        required=False,
        write_only=True,
    )
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta(BaseModelSerializer.Meta):
        model = Product
        fields = BaseModelSerializer.Meta.fields + (
            "name",
            "sku",
            "category",
            "category_name",
            "supplier",
            "supplier_name",
            "supplier_links",
            "supplier_ids",
            "price",
            "stock",
            "low_stock_threshold",
            "is_low_stock",
        )

    def validate_sku(self, value):
        value = value.strip().upper()

        if any(char.isspace() for char in value):
            raise serializers.ValidationError("SKU bosluk icermemelidir.")

        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Fiyat 0'dan buyuk olmalidir.")

        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stok negatif olamaz.")

        return value

    def validate_low_stock_threshold(self, value):
        if value < 0:
            raise serializers.ValidationError("Dusuk stok esigi negatif olamaz.")

        return value

    def validate(self, attrs):
        category = attrs.get("category")
        supplier = attrs.get("supplier")

        if category and not category.is_active:
            raise serializers.ValidationError(
                {"category": "Pasif kategori ile urun olusturulamaz."}
            )

        if supplier and not supplier.is_active:
            raise serializers.ValidationError(
                {"supplier": "Pasif tedarikci ile urun olusturulamaz."}
            )

        return attrs

    def create(self, validated_data):
        supplier_ids = validated_data.pop("supplier_ids", [])
        product = Product.objects.create(**validated_data)
        suppliers = {product.supplier, *supplier_ids}

        for supplier in suppliers:
            ProductSupplier.objects.get_or_create(
                product=product,
                supplier=supplier,
                defaults={"is_preferred": supplier.id == product.supplier_id},
            )

        return product

    def update(self, instance, validated_data):
        supplier_ids = validated_data.pop("supplier_ids", None)
        product = super().update(instance, validated_data)

        if supplier_ids is not None:
            suppliers = {product.supplier, *supplier_ids}

            for supplier in suppliers:
                ProductSupplier.objects.get_or_create(
                    product=product,
                    supplier=supplier,
                    defaults={"is_preferred": supplier.id == product.supplier_id},
                )

        return product
