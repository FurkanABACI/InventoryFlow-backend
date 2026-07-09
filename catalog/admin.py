from django.contrib import admin

from .models import Category, Product, ProductSupplier, Supplier


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active", "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("is_active",)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "sector", "email", "phone", "is_active")
    search_fields = ("name", "sector", "email", "phone")
    list_filter = ("sector", "is_active")

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "sku",
        "category",
        "supplier",
        "price",
        "stock",
        "low_stock_threshold",
        "is_active",
    )
    search_fields = ("name", "sku")
    list_filter = ("category", "supplier", "is_active")


@admin.register(ProductSupplier)
class ProductSupplierAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "supplier", "unit_cost", "is_preferred", "is_active")
    search_fields = ("product__name", "product__sku", "supplier__name")
    list_filter = ("supplier", "is_preferred", "is_active")
