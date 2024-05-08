from typing import TYPE_CHECKING

from dirtyfields import DirtyFieldsMixin
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Manager


def user_avatar_path(instance: AbstractUser, filename: str) -> str:
    """
    Функция определения пути аватара пользователя.

    :param instance: Экземпляр модели User.
    :param filename: Название файла.
    :return: Путь для сохранения аватара пользователя.
    """
    return 'users/user_{user_path}/avatars/user_avatar.jpg'.format(
        user_path="user_" + str(instance.username),
    )


def user_avatar_path_default() -> str:
    """
    Функция определения пути стандартного аватара.

    :return: Путь стандартного аватара.
    """
    return "users/users_default_avatar.jpg"


class CustomAccount(AbstractUser, DirtyFieldsMixin):
    """
    Расширение модели пользователя добавлением роли модератора и аватара пользователя.
    """
    avatar = models.ImageField(
        upload_to=user_avatar_path,
        null=True,
        blank=True
    )
    is_moderator = models.BooleanField(default=False)

    @property
    def default_avatar(self):
        """
        Возвращает путь к стандартному аватару, если у пользователя нет собственного аватара.

        :return: Путь к стандартному аватару.
        """
        return user_avatar_path_default()

    def set_password(self, raw_password):
        """
        Устанавливает пароль пользователя, хэшируя его.

        :param raw_password: Пароль в "сыром" виде.
        """
        self.password = make_password(raw_password)

    def save(self, *args, **kwargs):
        """
        Переопределяет метод сохранения пользователя.
        Если объект новый или пароль был изменен, устанавливает хэшированный пароль.
        Если объект новый и нет аватара, устанавливает стандартный аватар.
        Если объект удаляет аватар, устанавливает стандартный.
        """
        dirty_fields = self.get_dirty_fields()
        if (not self.pk) and (self.is_superuser is True):
            self.password = self.password
        elif 'password' in dirty_fields:
            self.set_password(self.password)

        if not self.pk and not self.avatar:
            self.avatar = self.default_avatar

        elif self.pk:
            old_avatar = CustomAccount.objects.get(pk=self.pk).avatar

            if not self.avatar and old_avatar != self.default_avatar:
                self.avatar = self.default_avatar
                old_avatar.delete(save=False)

            elif not self.avatar and old_avatar == self.default_avatar:
                self.avatar = self.default_avatar

        super().save(*args, **kwargs)


class PasswordResetRequest(models.Model):
    """
    Модель для сброса пароля.
    """
    email = models.EmailField(max_length=254)
    reset_code = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password reset request for {self.email}"

    if TYPE_CHECKING:
        objects: Manager
