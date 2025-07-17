# Generated manually to fix image_gif field length with SQL

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0010_increase_image_gif_length'),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE machines_machine ALTER COLUMN image_gif TYPE VARCHAR(500);",
            reverse_sql="ALTER TABLE machines_machine ALTER COLUMN image_gif TYPE VARCHAR(100);"
        ),
    ]