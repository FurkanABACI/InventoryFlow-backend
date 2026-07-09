from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0002_alter_category_is_active_alter_product_is_active_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="supplier",
            name="address",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="supplier",
            name="note",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="supplier",
            name="sector",
            field=models.CharField(blank=True, db_index=True, max_length=120),
        ),
    ]
