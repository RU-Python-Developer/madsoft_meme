from os import environ
from settings.config import settings
from sqlalchemy import create_engine
import psycopg2
from psycopg2 import Error


import databases


TESTING = environ.get("TESTING")
DB_USER = settings.DB_USER
DB_PASSWORD = settings.DB_PASSWORD
DB_HOST = settings.DB_HOST

if TESTING:
    # Use separate DB for tests
    DB_NAME = "test_db"
else:
    DB_NAME = settings.DB_NAME

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"
)
database = databases.Database(SQLALCHEMY_DATABASE_URL)
engine = create_engine(SQLALCHEMY_DATABASE_URL)


def extension_query(query):
    """Метод реализует пярмые запросы к БД"""
    global connection, cursor
    try:
        connection = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port="5432",
            database="test_db",
        )
        cursor = connection.cursor()

        cursor.execute(query)
        connection.commit()
        print("CONNECTION")

    except (Exception, Error) as error:
        print("Error connect", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Connect close")
