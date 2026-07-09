import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("catalog", "0002_alter_category_is_active_alter_product_is_active_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="GoodsReceipt",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("document_no", models.CharField(blank=True, db_index=True, max_length=100)),
                ("note", models.TextField(blank=True)),
                ("received_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("supplier", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="goods_receipts", to="catalog.supplier")),
            ],
            options={
                "ordering": ["-received_at"],
                "indexes": [
                    models.Index(fields=["supplier", "received_at"], name="recv_gr_supplier_date_idx"),
                    models.Index(fields=["received_at", "is_active"], name="recv_gr_date_active_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="GoodsReceiptItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("quantity", models.PositiveIntegerField()),
                ("unit_cost", models.DecimalField(decimal_places=2, max_digits=10)),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="goods_receipt_items", to="catalog.product")),
                ("receipt", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="receiving.goodsreceipt")),
            ],
            options={
                "ordering": ["id"],
            },
        ),
    ]
