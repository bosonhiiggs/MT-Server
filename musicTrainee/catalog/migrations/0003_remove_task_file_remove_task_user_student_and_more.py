# Generated by Django 5.0.3 on 2024-05-22 20:23

import catalog.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_task_user_student'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='file',
        ),
        migrations.RemoveField(
            model_name='task',
            name='user_student',
        ),
        migrations.CreateModel(
            name='TaskSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=catalog.models.course_tasks_directory_path)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to=settings.AUTH_USER_MODEL)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='catalog.task')),
            ],
            options={
                'ordering': ['-submitted_at'],
                'unique_together': {('task', 'student')},
            },
        ),
    ]