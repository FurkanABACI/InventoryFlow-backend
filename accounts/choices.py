from django.db import models


class UserRole(models.TextChoices):
    ADMIN = "admin", "Admin"
    OPERATIONS = "operations", "İdari İşler"
    DEPARTMENT = "department", "Birim Kullanıcısı"
