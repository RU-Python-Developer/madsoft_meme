FROM python:3.10-slim-buster

ENV PYTHONUNBUFFERED=1 \ 
    POETRY_VERSION=1.3.2

WORKDIR /backend

RUN pip install "poetry==$POETRY_VERSION"
COPY poetry.lock pyproject.toml /backend/
RUN poetry config virtualenvs.create false && poetry install

COPY . /backend
EXPOSE 8000

