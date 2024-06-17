from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Manager
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from .fields import OrderField
from django.conf import settings


def course_logo_directory_path(instance: "Course", filename: str) -> str:
    """
    Функция определения пути логотипа курса.

    :param instance: Экземпляр модели Course.
    :param filename: Название файла.
    :return: Путь для сохранения логотипа.
    """
    return "courses/course_{pk}/logo/{filename}".format(
        pk=instance.pk,
        filename=filename
    )


def course_images_directory_path(instance: "Course", filename: str) -> str:
    """
    Функция определения пути изображения для занятий.

    :param instance: Экземпляр модели Course.
    :param filename: Название файла.
    :return: Путь для сохранения изображений.
    """
    return "courses/course_{pk}/images/{filename}".format(
        pk=instance.pk,
        filename=filename
    )


def course_files_directory_path(instance: "Course", filename: str) -> str:
    """
    Функция определения пути прикладных файлов.

    :param instance: Выбранный курс.
    :param filename: Название файла.
    :return: Путь для сохранения файлов.
    """
    return "courses/course_{pk}/files/{filename}".format(
        pk=instance.pk,
        filename=filename
    )


class Course(models.Model):
    """
    Модель курса.
    """
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="courses_creator", on_delete=models.CASCADE)
    owner = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="courses_owner")
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    target_description = models.CharField(max_length=500)
    price = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    logo = models.ImageField(null=True, blank=True, upload_to=course_logo_directory_path)
    approval = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title}"

    if TYPE_CHECKING:
        objects: Manager


class Module(models.Model):
    """
    Модель модуля курса.
    """
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    order = OrderField(blank=True, for_fields=['course'])

    if TYPE_CHECKING:
        objects: Manager

    def __str__(self):
        return f'{self.order}. {self.title}'

    class Meta:
        ordering = ['order']


class Lesson(models.Model):
    module = models.ForeignKey(Module, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    order = OrderField(blank=True, for_fields=['module'])

    if TYPE_CHECKING:
        objects: Manager

    def __str__(self):
        return f'{self.order}. {self.title}'

    class Meta:
        ordering = ['order']


class Content(models.Model):
    """
    Модель контента курса.
    """
    lesson = models.ForeignKey(Lesson, related_name='contents', on_delete=models.CASCADE)
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
    order = OrderField(blank=True, for_fields=['lesson'])

    if TYPE_CHECKING:
        objects: Manager

    class Meta:
        ordering = ['order']


class ItemBase(models.Model):
    """
    Абстрактная базовая модель контента.
    """
    title = models.CharField(max_length=250)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class Text(ItemBase):
    """
    Модель текстового контента.
    """
    content = models.TextField()


class File(ItemBase):
    """
    Модель файла контента.
    """
    file = models.FileField(upload_to=course_files_directory_path)


class Image(ItemBase):
    """
    Модель изображения контента.
    """
    file = models.FileField(upload_to=course_images_directory_path)


class Video(ItemBase):
    """
    Модель видео контента.
    """
    url = models.URLField()


class Question(ItemBase):
    """
    Модель текста вопроса теста.
    """
    text = models.TextField(max_length=3000, verbose_name="text_question")

    # def __str__(self):
    #     return self.text


class Answer(models.Model):
    """
    Модель текста ответа теста.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=300)
    is_true = models.BooleanField(default=False)

    # def __str__(self):
    #     return self.text


def course_tasks_directory_path(instance: "Course", filename: str):
    """
    Функция определения пути сохранения заданий курса.

    :param instance: Экземпляр модели Course.
    :param filename: Название файла.
    :return: Путь для сохранения файла.
    """
    return "courses/course_{pk}/tasks/{filename}".format(
        pk=instance.pk,
        filename=filename
    )


class Task(ItemBase):
    """
    Модель задания курса.
    """
    description = models.TextField()

    def __str__(self):
        return f"{self.title}"

    if TYPE_CHECKING:
        objects: Manager


class TaskSubmission(models.Model):
    """
    Модель для прикрепления файла для проверки задания
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions")
    file = models.FileField(upload_to=course_tasks_directory_path)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("task", "student")
        ordering = ["-submitted_at"]

    if TYPE_CHECKING:
        objects: Manager


class TaskReview(models.Model):
    """
    Модель для ответа на домашнее задание пользователя
    """
    task_submission = models.ForeignKey(TaskSubmission, on_delete=models.CASCADE, related_name="review")
    is_correct = models.BooleanField(null=True, default=None)
    comment = models.TextField(blank=True)

    if TYPE_CHECKING:
        objects: Manager
