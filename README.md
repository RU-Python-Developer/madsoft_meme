Инструкция по установке и использованию приложения для работы с коллекцией мемов

# 1. Установка
## 1.1. Создание тома Server в docker:
```
docker volume create Server
```

## 1.2. Запуск сборки и старт контейнеров
```
docker compose up -d --build
```

## 1.3. Настройка Minio
- На странице [http://localhost:9001/](http://localhost:9001/), авторизируйтесь используя учетные данные: логин - tech, пароль - minio123
- На странице [http://localhost:9001/access-keys/new-account](http://localhost:9001/access-keys/new-account) создайте новый ключ доступа
- Установите соответствующие параметры ключа доступа в файле \backend\settings\config.py 
- - Access Key -> MINIO access_key
- - Secret Key -> MINIO secret_key

## 1.4. Пересборка контейнера backend

```
docker compose up backend -d --build
```

# 2. Использование 
Сервер доступен на странице FastApi-Swagger UI по адресу [http://localhost:5000/docs#](http://localhost:5000/docs#)

Логин - "admin", пароль - "qBpC4t", для доступа к приватной части сервера.

# 3. Тестирование
```
docker compose exec backend bash
```
```
python -m pytest
```