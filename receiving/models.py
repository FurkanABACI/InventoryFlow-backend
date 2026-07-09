from django.db import models

from catalog.models import Product, Supplier
from core.models import BaseModel


class GoodsReceipt(BaseModel):
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="goods_receipts",
    )
    document_no = models.CharField(max_length=100, blank=True, db_index=True)
    note = models.TextField(blank=True)
    received_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-received_at"]
        indexes = [
            models.Index(fields=["supplier", "received_at"]),
            models.Index(fields=["received_at", "is_active"]),
        ]

    def __str__(self):
        return f"Mal kabul #{self.id} - {self.supplier.name}"


class GoodsReceiptItem(BaseModel):
    receipt = models.ForeignKey(
        GoodsReceipt,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="goods_receipt_items",
    )
    quantity = models.PositiveIntegerField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
