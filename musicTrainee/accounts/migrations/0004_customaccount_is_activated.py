# Generated by Django 5.0.3 on 2024-06-20 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_passwordresetrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='customaccount',
            name='is_activated',
            field=models.BooleanField(default=False),
        ),
    ]
