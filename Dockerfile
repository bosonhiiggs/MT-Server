FROM python:3.10

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --upgrade pip poetry
RUN poetry config virtualenvs.create false --local
COPY poetry.lock pyproject.toml ./
RUN poetry install

RUN poetry show

COPY musicTrainee .

CMD ["gunicorn", "musicTrainee.wsgi:application", "--bind", "0.0.0.0:8000"]
