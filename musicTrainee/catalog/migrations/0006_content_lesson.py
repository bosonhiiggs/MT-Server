# Generated by Django 5.0.3 on 2024-06-01 12:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0005_lesson'),
    ]

    operations = [
        migrations.AddField(
            model_name='content',
            name='lesson',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contents', to='catalog.lesson'),
        ),
    ]
