from django.db import models


class StockRequestStatus(models.TextChoices):
    PENDING = "pending", "Bekliyor"
    PURCHASE_NEEDED = "purchase_needed", "Tedarik bekliyor"
    FULFILLED = "fulfilled", "Teslim edildi"
    CANCELLED = "cancelled", "İptal edildi"
