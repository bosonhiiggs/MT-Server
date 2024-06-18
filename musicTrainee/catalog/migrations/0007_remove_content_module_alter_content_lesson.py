# Generated by Django 5.0.3 on 2024-06-01 12:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0006_content_lesson'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='content',
            name='module',
        ),
        migrations.AlterField(
            model_name='content',
            name='lesson',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contents', to='catalog.lesson'),
        ),
    ]