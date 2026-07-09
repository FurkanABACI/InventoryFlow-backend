from django.db import models


class StockMovementType(models.TextChoices):
    IN = "in", "Giriş"
    OUT = "out", "Çıkış"
