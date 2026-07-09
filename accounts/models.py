from django.db import models

from accounts.choices import UserRole
from core.models import BaseModel


class UserProfile(BaseModel):
    user = models.OneToOneField(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="profile",
    )
    department = models.CharField(max_length=120, blank=True, db_index=True)
    role = models.CharField(
        max_length=30,
        choices=UserRole.choices,
        default=UserRole.DEPARTMENT,
        db_index=True,
    )

    class Meta:
        ordering = ["user__username"]
        indexes = [
            models.Index(fields=["role", "is_active"]),
            models.Index(fields=["department", "is_active"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
