# Generated by Django 5.0.3 on 2024-04-02 14:55

import catalog.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to=catalog.models.course_logo_directory_path),
        ),
    ]
