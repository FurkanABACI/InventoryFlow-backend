from django.db import models

from core.models import BaseModel
from stock.choices import StockMovementType


class StockMovement(BaseModel):
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.PROTECT,
        related_name="stock_movements",
    )
    movement_type = models.CharField(
        max_length=10,
        choices=StockMovementType.choices,
        db_index=True,
    )
    quantity = models.PositiveIntegerField()
    unit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    source_type = models.CharField(max_length=40, blank=True, db_index=True)
    source_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["product", "created_at"]),
            models.Index(fields=["movement_type", "created_at"]),
            models.Index(fields=["source_type", "source_id"]),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.get_movement_type_display()} x {self.quantity}"
