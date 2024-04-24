# Generated by Django 5.0.3 on 2024-04-07 09:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0008_alter_module_course'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='course',
            old_name='create_date',
            new_name='created',
        ),
        migrations.AddField(
            model_name='course',
            name='creator',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='courses_creator', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='course',
            name='owner',
        ),
        migrations.AddField(
            model_name='course',
            name='owner',
            field=models.ManyToManyField(related_name='courses_owner', to=settings.AUTH_USER_MODEL),
        ),
    ]