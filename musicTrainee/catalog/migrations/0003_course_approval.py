# Generated by Django 5.0.3 on 2024-04-02 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_course_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='approval',
            field=models.BooleanField(default=False),
        ),
    ]