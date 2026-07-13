import django_filters
from django.db.models import F

from catalog.models import Category, Product, Supplier
from core.filters import BaseFilterSet


class CategoryFilter(BaseFilterSet):
    search_fields = ("name", "description")

    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Category
        fields = (
            "name",
            "is_active",
            "created_after",
            "created_before",
            "updated_after",
            "updated_before",
            "search",
        )


class SupplierFilter(BaseFilterSet):
    search_fields = ("name", "sector", "email", "phone", "address", "note")

    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    email = django_filters.CharFilter(field_name="email", lookup_expr="icontains")

    class Meta:
        model = Supplier
        fields = (
            "name",
            "email",
            "is_active",
            "created_after",
            "created_before",
            "updated_after",
            "updated_before",
            "search",
        )


class ProductFilter(BaseFilterSet):
    search_fields = ("name", "sku", "category__name", "supplier__name")

    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    sku = django_filters.CharFilter(field_name="sku", lookup_expr="icontains")
    category = django_filters.NumberFilter(field_name="category_id")
    supplier = django_filters.NumberFilter(field_name="supplier_id")
    stock_min = django_filters.NumberFilter(field_name="stock", lookup_expr="gte")
    stock_max = django_filters.NumberFilter(field_name="stock", lookup_expr="lte")
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    is_low_stock = django_filters.BooleanFilter(method="filter_is_low_stock")

    class Meta:
        model = Product
        fields = (
            "name",
            "sku",
            "category",
            "supplier",
            "stock_min",
            "stock_max",
            "price_min",
            "price_max",
            "is_active",
            "is_low_stock",
            "created_after",
            "created_before",
            "updated_after",
            "updated_before",
            "search",
        )

    def filter_is_low_stock(self, queryset, name, value):
        if value is True:
            return queryset.filter(stock__lte=F("low_stock_threshold"))

        if value is False:
            return queryset.filter(stock__gt=F("low_stock_threshold"))

        return queryset
