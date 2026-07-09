from django.db import models

from core.models import BaseModel


class Category(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Supplier(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    sector = models.CharField(max_length=120, blank=True, db_index=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    note = models.TextField(blank=True)

    class Meta:
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(BaseModel):
    name = models.CharField(max_length=255, db_index=True)
    sku = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(
        "catalog.Category",
        on_delete=models.PROTECT,
        related_name="products",
    )
    supplier = models.ForeignKey(
        "catalog.Supplier",
        on_delete=models.PROTECT,
        related_name="products",
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, db_index=True)
    stock = models.PositiveIntegerField(default=0, db_index=True)
    low_stock_threshold = models.PositiveIntegerField(default=5)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["supplier", "is_active"]),
        ]

    def __str__(self):
        return self.name

    @property
    def is_low_stock(self):
        return self.stock <= self.low_stock_threshold


class ProductSupplier(BaseModel):
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.CASCADE,
        related_name="supplier_links",
    )
    supplier = models.ForeignKey(
        "catalog.Supplier",
        on_delete=models.CASCADE,
        related_name="product_links",
    )
    unit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    is_preferred = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Product Supplier"
        verbose_name_plural = "Product Suppliers"
        ordering = ["product__name", "supplier__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "supplier"],
                name="unique_product_supplier",
            ),
        ]
        indexes = [
            models.Index(
                fields=["product", "is_active"],
                name="catalog_pro_product_a776ad_idx",
            ),
            models.Index(
                fields=["supplier", "is_active"],
                name="catalog_pro_supplier_30c36e_idx",
            ),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.supplier.name}"
