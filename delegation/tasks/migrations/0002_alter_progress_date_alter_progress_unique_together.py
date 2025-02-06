# Generated by Django 5.1.5 on 2025-01-29 21:26

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='progress',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterUniqueTogether(
            name='progress',
            unique_together={('assignment', 'date')},
        ),
    ]
