# Music Trainee - серверный модуль

Backend модуль веб-приложения Music Trainee. Данное приложение предназначено для изучения музыки и помощи начинающим 
преподавателям.

***Статус: Закрыт***

## Технологии
- Django: Python фреймворк для разработки backend части;
- SQLite: компактная СУБД для локальной разработки;
- Poetry: система контроля зависимостей;
- Docker: система автоматизации развертывания;
- NGINX: веб-сервер для загрузки статических файлов;

## Установка

1. Клонировать репозиторий:
    ```
    git clone https://github.com/bosonhiiggs/MT-Server.git
    ```
2. Копировать файл `.env.template`:
   ```
   cp .env.template .env
   ```
3. Отредактировать `.env` текстовым редактором (например, `nano`):
   ```
   nano .env
   ```
4. Установить Docker:
   ```
   pip install docker-ce
   ```
5. Собрать Docker контейнеры для `Django` и `NGINX` через `docker-compose`:
   ```
   docker compose build app 
   docker compose build nginx 
   ```
6. Выполнить миграции:
   ```
   docker compose exec app python manage.py migrate
   ```
7. (Опционально) Сделать `loaddata` из файла `db.json`:
   ```
   docker compose exec app python manage.py loaddata db.json
   ```   
8. Запустить Docker образы:
   ```
   docker compose up -d app
   docker compose up -d nginx
   ```
9. Перейти по пути:
   ```
   http://0.0.0.0:8000/
   ```
## Контакты
Если у вас есть вопросы, связанные с проектом, свяжитесь в телеграм: https://t.me/bosonhiggs992
