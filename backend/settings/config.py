from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    TESTING: bool = False
    MINIO: dict = {
        'endpoint': 'minio:9000',
        'access_key': '8sHkXxnDc6RW1CrN8HNC',
        'secret_key': 'Qh0NzyYaQfHKomT8M0yqXKcnEsEj0kWDsMIBNUsn'
    }
    TOKEN: str = 'p0qBw9zqvAAH7FNn3UNqBpC4t'
    PASSWORD: str = 'qBpC4t'
    HOST: list = [
        "http://localhost",
        "http://localhost:4200",
    ]
    DB_HOST: str = "db"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "Ngeom0booyae2hi7quuo8oonohxahVohzooja6"
    DB_NAME: str = "postgres"

#     register
    SECRET_KEY: str = "1efeb6e36a1d7a185f6759bf335be80c40b6e9f3ea79874329d90a00392ac5b412"
    ALGORITHM: str = "HS256"


settings = Settings()
