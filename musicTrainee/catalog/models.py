from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Manager
from django.contrib.auth.models import User


def course_logo_directory_path(instance: "Course", filename: str) -> str:
    return "courses/course_{pk}/logo/{filename}".format(
        pk=instance.pk,
        filename=filename
    )


class Course(models.Model):
    owner = models.ForeignKey(User, related_name="courses_created", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    price = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    create_date = models.DateTimeField(auto_now_add=True)
    logo = models.ImageField(null=True, blank=True, upload_to=course_logo_directory_path)
    approval = models.BooleanField(default=False)

    if TYPE_CHECKING:
        objects: Manager
