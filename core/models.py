from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_%(class)s_set",
    )
    updated_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_%(class)s_set",
    )
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        abstract = True

    def deactivate(self, user=None):
        self.is_active = False

        if user and user.is_authenticated:
            self.updated_by = user

        self.save(update_fields=["is_active", "updated_by", "updated_at"])

    def activate(self, user=None):
        self.is_active = True

        if user and user.is_authenticated:
            self.updated_by = user

        self.save(update_fields=["is_active", "updated_by", "updated_at"])
