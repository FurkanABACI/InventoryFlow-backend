from django.db import models

from core.models import BaseModel
from requisitions.choices import StockRequestStatus


class StockRequest(BaseModel):
    requester_user = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_requests",
    )
    department = models.CharField(max_length=120, db_index=True)
    requester_name = models.CharField(max_length=120)
    note = models.TextField(blank=True)
    status = models.CharField(
        max_length=30,
        choices=StockRequestStatus.choices,
        default=StockRequestStatus.PENDING,
        db_index=True,
    )
    fulfilled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["requester_user", "created_at"]),
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["department", "created_at"]),
        ]

    def __str__(self):
        return f"{self.department} - {self.requester_name}"


class StockRequestItem(BaseModel):
    request = models.ForeignKey(
        "requisitions.StockRequest",
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.PROTECT,
        related_name="stock_request_items",
    )
    quantity = models.PositiveIntegerField()
    delivered_quantity = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
