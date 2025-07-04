# Generated by Django 4.2.7 on 2025-07-02 22:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ModeEntrainement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Date de modification')),
                ('nom', models.CharField(choices=[('FORCE', 'Force'), ('PRISE_MASSE', 'Prise de masse'), ('SECHE', 'Sèche'), ('ENDURANCE', 'Endurance'), ('POWERLIFTING', 'Powerlifting')], max_length=50, unique=True, verbose_name='Nom du mode')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('series_recommandees', models.PositiveIntegerField(default=3, verbose_name='Nombre de séries recommandées')),
                ('repetitions_min', models.PositiveIntegerField(default=1, verbose_name='Répétitions minimum')),
                ('repetitions_max', models.PositiveIntegerField(default=15, verbose_name='Répétitions maximum')),
                ('repos_entre_series', models.PositiveIntegerField(default=90, help_text='Temps de repos en secondes', verbose_name='Repos entre séries (s)')),
                ('pourcentage_1rm_min', models.FloatField(default=0.6, verbose_name='% 1RM minimum')),
                ('pourcentage_1rm_max', models.FloatField(default=0.9, verbose_name='% 1RM maximum')),
                ('is_active', models.BooleanField(default=True, verbose_name='Actif')),
            ],
            options={
                'verbose_name': "Mode d'entraînement",
                'verbose_name_plural': "Modes d'entraînement",
                'ordering': ['nom'],
            },
        ),
    ]
