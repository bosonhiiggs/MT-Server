from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Manager
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


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


class Module(models.Model):
    owner = models.OneToOneField(Course, related_name="modules", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)


class Content(models.Model):
    owner = models.ForeignKey(Module, related_name='contents', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     limit_choices_to={
                                         'model__in':(
                                             'text',
                                             'video',
                                             'image',
                                             'file',
                                         )
                                     }
                                     )
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')


class ItemBase(models.Model):
    title = models.CharField(max_length=250)
    # created = models.DateTimeField(auto_now_add=True)
    # update = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class Text(ItemBase):
    content = models.TextField()


def course_files_directory_path(instance: Course, filename: str) -> str:
    return "courses/course_{pk}/files/{filename}".format(
        pk=instance.pk,
        filename=filename
    )


class File(ItemBase):
    file = models.FileField(upload_to=course_files_directory_path)


def course_images_directory_path(instance: Course, filename: str) -> str:
    return "courses/course_{pk}/images/{filename}".format(
        pk=instance.pk,
        filename=filename
    )


class Image(ItemBase):
    file = models.FileField(upload_to=course_images_directory_path)


class Video(ItemBase):
    url = models.URLField()

