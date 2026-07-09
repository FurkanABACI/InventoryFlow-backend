from django.contrib import admin

from receiving.models import GoodsReceipt, GoodsReceiptItem


class GoodsReceiptItemInline(admin.TabularInline):
    model = GoodsReceiptItem
    extra = 0


@admin.register(GoodsReceipt)
class GoodsReceiptAdmin(admin.ModelAdmin):
    list_display = ("id", "supplier", "document_no", "received_at", "is_active")
    list_filter = ("supplier", "is_active")
    search_fields = ("supplier__name", "document_no")
    inlines = (GoodsReceiptItemInline,)
