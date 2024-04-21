from django.contrib.auth.models import AbstractUser, User
from django.db import models


def user_avatar_path(instance: User, filename: str) -> str:
    return 'users/user_{user_path}/avatars/user_default_avatar.jpg'.format(
        user_path="user_" + str(instance.username),
    )


def user_avatar_path_default() -> str:
    return "users/user_default_avatar.jpg"


class CustomAccount(AbstractUser):
    # Расширение модели пользователя
    avatar = models.ImageField(
        upload_to=user_avatar_path,
        default=user_avatar_path_default,
        null=True,
        blank=True
    )
    is_moderator = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.avatar = user_avatar_path_default()
        super().save(*args, **kwargs)

