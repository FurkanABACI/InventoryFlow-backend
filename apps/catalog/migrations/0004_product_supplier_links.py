import django.db.models.deletion
from django.db import migrations, models


def create_existing_product_supplier_links(apps, schema_editor):
    Product = apps.get_model("catalog", "Product")
    ProductSupplier = apps.get_model("catalog", "ProductSupplier")

    for product in Product.objects.all():
        ProductSupplier.objects.get_or_create(
            product_id=product.id,
            supplier_id=product.supplier_id,
            defaults={
                "is_preferred": True,
                "is_active": True,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0003_supplier_address_supplier_note_supplier_sector"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductSupplier",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("unit_cost", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("is_preferred", models.BooleanField(default=False)),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="supplier_links", to="catalog.product")),
                ("supplier", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="product_links", to="catalog.supplier")),
            ],
            options={
                "verbose_name": "Product Supplier",
                "verbose_name_plural": "Product Suppliers",
                "ordering": ["product__name", "supplier__name"],
                "indexes": [
                    models.Index(fields=["product", "is_active"], name="catalog_pro_product_a776ad_idx"),
                    models.Index(fields=["supplier", "is_active"], name="catalog_pro_supplier_30c36e_idx"),
                ],
            },
        ),
        migrations.AddConstraint(
            model_name="productsupplier",
            constraint=models.UniqueConstraint(fields=("product", "supplier"), name="unique_product_supplier"),
        ),
        migrations.RunPython(
            create_existing_product_supplier_links,
            migrations.RunPython.noop,
        ),
    ]
