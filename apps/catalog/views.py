from django.db.models import F

from rest_framework.decorators import action
from rest_framework.response import Response

from apps.catalog.filters import CategoryFilter, ProductFilter, SupplierFilter
from apps.catalog.models import Category, Product, ProductSupplier, Supplier
from apps.catalog.serializers import (
    CategorySerializer,
    CategoryWithProductsSerializer,
    ProductSupplierSerializer,
    ProductSerializer,
    SupplierSerializer,
)
from apps.core.views import BaseModelViewSet


class CategoryViewSet(BaseModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filterset_class = CategoryFilter

    @action(detail=False, methods=["get"], url_path="with-products")
    def with_products(self, request):
        queryset = self.filter_queryset(
            self.get_queryset().prefetch_related("products")
        )
        serializer = CategoryWithProductsSerializer(queryset, many=True)
        return Response(serializer.data)


class SupplierViewSet(BaseModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    filterset_class = SupplierFilter


class ProductViewSet(BaseModelViewSet):
    queryset = Product.objects.select_related("category", "supplier").prefetch_related(
        "supplier_links__supplier",
    ).all()
    serializer_class = ProductSerializer
    filterset_class = ProductFilter

    @action(detail=False, methods=["get"], url_path="low-stock")
    def low_stock(self, request):
        queryset = self.filter_queryset(
            self.get_queryset().filter(stock__lte=F("low_stock_threshold"))
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="deactivate")
    def deactivate(self, request, pk=None):
        product = self.get_object()
        product.is_active = False
        product.save(update_fields=["is_active", "updated_at"])
        serializer = self.get_serializer(product)
        return Response(serializer.data)


class ProductSupplierViewSet(BaseModelViewSet):
    queryset = ProductSupplier.objects.select_related("product", "supplier").all()
    serializer_class = ProductSupplierSerializer
