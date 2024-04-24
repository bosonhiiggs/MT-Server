"""
Этот модуль предоставляет общие функциональные возможности, используемые другими модулями.
"""

import secrets
import string

from django.core.mail import send_mail


def generate_reset_code(length=8):
    """
    Функция определения кода восстановления.

    :param length: Длина кода восстановления.
    :return: Код восстановления.
    """
    characters = string.ascii_uppercase + string.digits
    reset_code = ''.join(secrets.choice(characters) for _ in range(length))
    return reset_code


def send_reset_code_email(email, reset_code):
    """
    Функция отправления письма с кодом восстановления.

    :param email: Почта пользователя.
    :param reset_code: Код восстановления.
    """
    subject = f'Сброс пароля'
    message = f'Ваш код для сброса пароля: {reset_code}'
    from_email = 'yourmail@example.com'
    recipient_list = [email]
    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=recipient_list,
    )
