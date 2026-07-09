from django.contrib import admin

from accounts.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "department", "is_active")
    list_filter = ("role", "department", "is_active")
    search_fields = ("user__username", "user__email", "department")
