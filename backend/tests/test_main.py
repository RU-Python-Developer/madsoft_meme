import logging
import os

import pytest
from minio import Minio
from fastapi.testclient import TestClient
from httpx import AsyncClient, BasicAuth
from sqlalchemy_utils import create_database, drop_database, database_exists
from alembic import command
from alembic.config import Config

os.environ["TESTING"] = "True"
from models import database
from main import app

from settings.config import settings
from schemas import memes
from routers import memes_private

client = TestClient(app)

client_minio = Minio(settings.MINIO['endpoint'],
                     access_key=settings.MINIO['access_key'],
                     secret_key=settings.MINIO['secret_key'],
                     secure=False
                     )
bucket_name = 'test-bucket'


def login():
    """Авторизация пользователя"""
    return memes_private.create_access_token(), "bearer"


def set_data(query):
    """Установка тестовых данных в BD"""
    database.extension_query(query=query)


def set_img(path: str):
    """Установка тестового изображения в хранилище"""
    found = client_minio.bucket_exists(bucket_name)
    if not found:
        client_minio.make_bucket(bucket_name)

    client_minio.fput_object(
        bucket_name, 'img_test.png', path,
    )


def delete_test_bucket():
    """Очистка и удаление корзины после тестирования"""
    found = client_minio.bucket_exists(bucket_name)
    if found:
        objects = client_minio.list_objects(bucket_name)
        for obj in objects:
            client_minio.remove_object(bucket_name, obj.object_name)

        client_minio.remove_bucket(bucket_name)


def create_db():
    """Создание тестовой (test_db) DB для тестирования"""
    if not database_exists(database.SQLALCHEMY_DATABASE_URL):
        create_database(database.SQLALCHEMY_DATABASE_URL)

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    alembic_cfg = Config(os.path.join(base_dir + '/backend', "alembic.ini"))
    command.upgrade(alembic_cfg, "head")


def db_async(func):
    """ - Создание и коннект с BD перед тестированием.
        - Закрытие соединениея и удаление BD после теста.
        - Очистка и удаление корзины.
    """
    async def wrapped():
        create_db()
        try:
            await database.database.connect()
            await func()
            await database.database.disconnect()
        finally:
            drop_database(database.SQLALCHEMY_DATABASE_URL)
            delete_test_bucket()
    return wrapped


@db_async
async def test_get_meme():
    """Тестирование публичного эндпоинта - получение мема по id"""
    set_data(
        'INSERT INTO "memes" (name, bucket_name, description, created_at) '
        f'VALUES (\'img_test.png\', \'{bucket_name}\', \'Тестовый мем\',\'2024-07-04T11:09:32.219736\');')
    set_img(path='tests/tmp/img_test.png')

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        id_meme = '1'
        res = await async_client.get("/memes/" + id_meme)
        print('text', res.json()['created_at'])
        assert res.status_code == 200
        assert res.json()['id'] == 1
        assert res.json()['name'] == 'img_test.png'
        assert res.json()['bucket_name'] == bucket_name
        assert res.json()['description'] == 'Тестовый мем'
        assert res.json()['created_at'] == '2024-07-04T11:09:32.219736'


@db_async
async def test_not_valid_index():
    """Тестирование получения данных с невалидными индексами в приватной и публичной части"""
    set_data(
        'INSERT INTO "memes" (name, bucket_name, description, created_at) '
        f'VALUES (\'img_test.png\', \'{bucket_name}\', \'Тестовый мем\',\'2024-07-04T11:09:32.219736\');')
    set_img(path='tests/tmp/img_test.png')

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        access_token, token_type = login()
        headers = {"Authorization": f'{token_type} {access_token}'}

        inx = 2
        url = f'/memes/{inx}'
        error_msg = {'detail': f'Error 500: IndexError - There is no data with index {inx}'}

        endpoint_use_index = {'get': [url, None, headers],
                              'put': [url, {"description": "Обновление описания"}, headers],
                              'delete': [url, None, headers]}

        for request_type, request_data in endpoint_use_index.items():
            url = request_data[0]
            data = request_data[1]
            headers = request_data[2]

            match request_type:
                case 'get':
                    res = await async_client.get(url, headers=headers)
                case 'put':
                    res = await async_client.put(url, data=data, headers=headers)
                case 'delete':
                    res = await async_client.delete(url, headers=headers)

            assert res.json() == error_msg
