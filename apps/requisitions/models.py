from django.db import models

from apps.catalog.models import Product
from apps.core.models import BaseModel


class StockRequest(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Bekliyor"
        PURCHASE_NEEDED = "purchase_needed", "Tedarik bekliyor"
        FULFILLED = "fulfilled", "Teslim edildi"
        CANCELLED = "cancelled", "İptal edildi"

    department = models.CharField(max_length=120, db_index=True)
    requester_name = models.CharField(max_length=120)
    note = models.TextField(blank=True)
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    fulfilled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["department", "created_at"]),
        ]

    def __str__(self):
        return f"{self.department} - {self.requester_name}"


class StockRequestItem(BaseModel):
    request = models.ForeignKey(
        StockRequest,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="stock_request_items",
    )
    quantity = models.PositiveIntegerField()
    delivered_quantity = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

