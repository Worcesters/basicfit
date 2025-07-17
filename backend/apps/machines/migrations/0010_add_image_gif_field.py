# Generated manually to add image_gif field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0009_update_cardio_machines_to_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='machine',
            name='image_gif',
            field=models.URLField(
                blank=True,
                help_text='URL de l\'animation GIF sur Cloudinary',
                max_length=500,
                null=True,
                verbose_name='Animation GIF (URL Cloudinary)'
            ),
        ),
    ]