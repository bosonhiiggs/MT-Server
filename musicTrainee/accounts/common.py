"""
Этот модуль предоставляет общие функциональные возможности, используемые другими модулями.
"""

import secrets
import string

from django.conf import settings
from django.core.mail import send_mail

# from musicTrainee import settings

def generate_reset_code(length=6):
    """
    Функция определения кода восстановления.

    :param length: Длина кода восстановления.
    :return: Код восстановления.
    """
    reset_code = ''.join(secrets.choice(string.digits) for _ in range(length))
    return reset_code


def send_reset_code_email(email, reset_code):
    """
    Функция отправления письма с кодом восстановления на указанную почту.

    :param email: Почта пользователя.
    :param reset_code: Код восстановления.
    """
    subject = f'Music Trainee запрос на сброс пароля'
    message = (f'Здравствуйте!'
               f'Ваш код для сброса пароля: {reset_code}'
               )
    # from_email = settings.EMAIL_HOST_USER
    from_email = 'pyaninyury@yandex.ru'
    recipient_list = [email]
    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=recipient_list,
    )


def send_confirm_code_email(email, confirm_code):
    """
    Функция отправления письма с кодом восстановления на указанную почту.

    :param confirm_code: Код подтверждения
    :param email: Почта пользователя.
    """
    subject = f'Music Trainee подтверждение учетной записи'
    message = (f'Здравствуйте!\n'
               f'Ваш код для подтверждения учетной пароля: {confirm_code}'
               )
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=recipient_list,
    )
