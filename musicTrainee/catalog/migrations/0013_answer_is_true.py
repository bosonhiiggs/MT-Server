# Generated by Django 5.0.3 on 2024-04-07 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0012_question_task_rename_content_file_file_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='is_true',
            field=models.BooleanField(default=False),
        ),
    ]