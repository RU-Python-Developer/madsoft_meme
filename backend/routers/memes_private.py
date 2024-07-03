from datetime import datetime, timedelta, timezone
from typing import Annotated
import io

from fastapi import APIRouter, HTTPException, UploadFile, Depends, status, File, Form, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from minio import Minio
from typing import List
from jose import JWTError, jwt
from pydantic import ValidationError

from crud import memes as crud
from schemas import memes
from settings.config import settings

router = APIRouter()

client = Minio(settings.MINIO['endpoint'],
               access_key=settings.MINIO['access_key'],
               secret_key=settings.MINIO['secret_key'],
               secure=False
               )
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def create_access_token():
    """Создание токена"""
    to_encode = {"sub": settings.TOKEN}
    expires_delta = timedelta(minutes=1440)
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """Извлечение данных из токена"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        log: str = payload.get("sub")
        if log is None:
            raise credentials_exception
        token_data = memes.TokenData(log=log)
    except JWTError:
        raise credentials_exception
    user = check_token(secret_key=token_data.log)
    if user is None:
        raise credentials_exception
    return user


def check_token(secret_key: str):
    """Проверка корректности извлеченного токена"""
    if secret_key != settings.TOKEN:
        raise credentials_exception
    return {'name': 'admin'}


@router.post("/token")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> memes.Token | bool:
    """Авторизация администратора"""
    if form_data.password == settings.PASSWORD and form_data.username == 'admin':
        return memes.Token(access_token=create_access_token(), token_type="bearer")
    else:
        return False


@router.get("/users/me/")
async def read_users_me(
        user: Annotated[memes.UserBase, Depends(get_current_user)],
):
    return user


@router.post("/memes")
async def upload_memes(
        user: Annotated[memes.UserBase, Depends(get_current_user)],
        bucket_name: str = Form(...),
        description: str = Form(...),
        file: List[UploadFile] = File(...)
):
    """Эндпоинт добавления нового мема (с картинкой и текстом)"""
    if user:
        byte_file = await file[0].read()
        source_file = io.BytesIO(byte_file)

        try:
            data = memes.UploadMemes(
                bucket_name=bucket_name,
                description=description
            )
            found = client.bucket_exists(data.bucket_name)
            if not found:
                client.make_bucket(data.bucket_name)

            upload_data = dict(
                name=file[0].filename,
                description=data.description,
                bucket_name=data.bucket_name,
                created_at=datetime.now()
            )
            meme_id = await crud.add_meme(upload_data)
            if meme_id:
                client.put_object(bucket_name, file[0].filename, source_file, length=len(byte_file))
        except ValidationError as exc:
            raise HTTPException(status_code=500, detail=f"ValidationError {repr(exc.errors()[0]['type'])}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error {e}")

        return meme_id or False
    else:
        raise credentials_exception


@router.put("/memes/{id}")
async def update_memes(
        user: Annotated[memes.UserBase, Depends(get_current_user)],
        id,
        description: str = Form(...),
        file: UploadFile = None
):
    """Эндпоинт обновления существующего мема"""
    global source_file, byte_file

    if user:
        try:
            data = memes.UpdateMeme(id=id, description=description)
        except ValidationError as exc:
            raise HTTPException(status_code=500, detail=f"ValidationError {repr(exc.errors()[0]['type'])}")
        if file:
            byte_file = await file.read()
            source_file = io.BytesIO(byte_file)
            data.set_attr('name', file.filename)

        try:
            result = await crud.update_meme(data=data, date=datetime.now())
            if not result:
                raise HTTPException(status_code=500, detail=f"IndexError - There is no data with index {data.id}")
            bucket_name, meme_name = result
            if meme_name and file:
                client.remove_object(bucket_name, meme_name)
                client.put_object(bucket_name, file.filename, source_file, length=len(byte_file))
                return meme_name
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error {e}")

        return meme_name or False
    else:
        raise credentials_exception


@router.delete("/memes/{id}")
async def delete_meme(
        user: Annotated[memes.UserBase, Depends(get_current_user)],
        id):
    """Эндпоинт удаления мема"""
    if user:
        try:
            data = memes.DeleteMeme(id=id)
            result = await crud.delete_meme(id_meme=data.id)
            if not result:
                raise HTTPException(status_code=500, detail=f"IndexError - There is no data with index {data.id}")
            bucket_name, meme_name = result
            if meme_name:
                client.remove_object(bucket_name, meme_name)
        except ValidationError as exc:
            raise HTTPException(status_code=500, detail=f"ValidationError {repr(exc.errors()[0]['type'])}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error {e}")

        return meme_name
    else:
        raise credentials_exception
