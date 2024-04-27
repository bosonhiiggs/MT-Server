# Music Trainee - серверный модуль

Backend модуль веб-приложения Music Trainee. Данное приложение предназначено для изучения музыки и помощи начинающим 
преподавателям.

***Статус: В разработке***

## Технологии
- Django: Python фреймворк для разработки backend части;
- SQLite: компактная СУБД для локальной разработки;
- Poetry: система контроля зависимостей.

## Установка

1. Клонировать репозиторий:
    ```
    git clone https://github.com/bosonhiiggs/MT-Server.git
    ```
2. Создать виртуальное окружение:
    ```
   python -m venv venv
   ```
3. Активировать виртуальное окружение:
   ```
   source venv/bin/activete
   ```
4. Установить зависимости через poetry:
   ```
   pip install poetry
   poetry install
   ```
5. Перейти в директорию проекта:
   ```
   cd musicTrainee
   ```
6. Применить миграции:
    ```
    python manage.py migrate
    ```
7. Запустить сервер:
   ```
    python manage.py runserver
   ```

## Контакты
Если у вас есть вопросы, связанные с проектом, свяжитесь в телеграм: https://t.me/bosonhiggs992
