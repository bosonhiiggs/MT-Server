from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Manager
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from .fields import OrderField
from django.conf import settings


def course_logo_directory_path(instance: "Course", filename: str) -> str:
    """
    Функция для описания пути логотипа курса
    :param instance: выбранный курс
    :param filename: название файла
    :return: путь для логотипа
    """
    return "courses/course_{pk}/logo/{filename}".format(
        pk=instance.pk,
        filename=filename
    )


def course_images_directory_path(instance: "Course", filename: str) -> str:
    """
    Функция для описания пути изображения для занятий
    :param instance: выбранный курс
    :param filename: название файла
    :return: путь для изображений
    """
    return "courses/course_{pk}/images/{filename}".format(
        pk=instance.pk,
        filename=filename
    )


def course_files_directory_path(instance: "Course", filename: str) -> str:
    """
    Функция для описания пути прикладных файлов
    :param instance: выбранный курс
    :param filename: название файла
    :return: путь для файлов
    """
    return "courses/course_{pk}/files/{filename}".format(
        pk=instance.pk,
        filename=filename
    )


class Course(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="courses_creator", on_delete=models.CASCADE)
    # creator = models.ForeignKey(User, related_name="courses_creator", on_delete=models.CASCADE)
    owner = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="courses_owner")
    # owner = models.ManyToManyField(User, blank=True, related_name="courses_owner")
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    price = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    logo = models.ImageField(null=True, blank=True, upload_to=course_logo_directory_path)
    approval = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title}"

    if TYPE_CHECKING:
        objects: Manager


class Module(models.Model):
    course = models.ForeignKey(Course, related_name="modules", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    order = OrderField(blank=True, for_fields=['course'])

    if TYPE_CHECKING:
        objects: Manager

    def __str__(self):
        return f'{self.order}. {self.title}'

    class Meta:
        ordering = ['order']


class Content(models.Model):
    module = models.ForeignKey(Module, related_name='contents', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     limit_choices_to={
                                         'model__in':
                                             (
                                                 'text',
                                                 'video',
                                                 'image',
                                                 'file',
                                                 'question',
                                                 'task',
                                             )
                                     }
                                     )
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module'])

    if TYPE_CHECKING:
        objects: Manager

    class Meta:
        ordering = ['order']


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


class File(ItemBase):
    file = models.FileField(upload_to=course_files_directory_path)


class Image(ItemBase):
    file = models.FileField(upload_to=course_images_directory_path)


class Video(ItemBase):
    url = models.URLField()


class Question(ItemBase):
    text = models.TextField(max_length=3000, verbose_name="text_question")

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=300)
    is_true = models.BooleanField(default=False)

    def __str__(self):
        return self.text


def course_tasks_directory_path(instance: "Course", filename: str):
    return "courses/course_{pk}/tasks/{filename}".format(
        pk=instance.pk,
        filename=filename
    )


class Task(ItemBase):
    description = models.TextField()
    file = models.FileField(blank=True, upload_to=course_tasks_directory_path)
