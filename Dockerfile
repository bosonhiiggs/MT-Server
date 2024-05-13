FROM python:3.10

# Устанавливает переменную окружения, которая гарантирует,
# что вывод из python будет отправлен прямо в терминал без предварительной буферизации.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip poetry
RUN poetry config virtualenvs.create false --local
COPY poetry.lock pyproject.toml ./
RUN poetry install

RUN poetry show

COPY musicTrainee .
RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "musicTrainee.wsgi:application", "--bind", "0.0.0.0:8001"]
#CMD ["cd", "musicTrainee", "&&", "python", "manage.py", "runserver"]
#CMD ["python", "musicTrainee.manage.py", "runserver"]
