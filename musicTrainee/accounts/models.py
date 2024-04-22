from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, User
from django.db import models


def user_avatar_path(instance: User, filename: str) -> str:
    return 'users/user_{user_path}/avatars/user_avatar.jpg'.format(
        user_path="user_" + str(instance.username),
    )


def user_avatar_path_default() -> str:
    return "users/users_default_avatar.jpg"


class CustomAccount(AbstractUser):
    # Добавление в модель пользователя роли модератора и фотографию пользователя
    avatar = models.ImageField(
        upload_to=user_avatar_path,
        # default=user_avatar_path_default,
        null=True,
        blank=True
    )
    is_moderator = models.BooleanField(default=False)

    @property
    def default_avatar(self):
        return user_avatar_path_default()

    def set_password(self, raw_password):
        # print(raw_password)
        # self.password = raw_password
        self.password = make_password(raw_password)

    def save(self, *args, **kwargs):
        if self.pk is None or 'password' not in self._state.fields_cache:
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



