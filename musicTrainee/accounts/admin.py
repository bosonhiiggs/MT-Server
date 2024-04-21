from django.contrib import admin
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

user_model = get_user_model()
print("Кастомная модель пользователя:", user_model)


@admin.register(user_model)
# class AccountAdmin(UserAdmin):
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'is_active',
        'is_staff',
        'avatar',
        'is_moderator',
    )
    # ordering = 'username'


# @admin.site.register(user_model)
# class AccountAdmin(UserAdmin):
    # ordering = 'username'