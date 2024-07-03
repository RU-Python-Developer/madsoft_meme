from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from minio import Minio
import base64

from crud import memes as crud
from settings.config import settings
from schemas import memes

router = APIRouter()

client = Minio(settings.MINIO['endpoint'],
               access_key=settings.MINIO['access_key'],
               secret_key=settings.MINIO['secret_key'],
               secure=False
               )


async def get_memes_from_minio(bucket_name: str, name: str) -> bytes:
    """Получение файла из хранилища"""
    global response
    try:
        response = client.get_object(bucket_name, name)
        if not response:
            raise HTTPException(status_code=404, detail=f"The {name} object in the {bucket_name} repository is missing")
        file = base64.b64encode(response.read())
    finally:
        response.close()
        response.release_conn()
    return file


@router.get("/memes/{id}")
async def get_meme(id):
    """Эндпоинт получения конкретного мема по id"""
    global data
    try:
        data = memes.GetMeme(id=id)
        result = await crud.get_meme(id_meme=data.id)

        if not result:
            raise HTTPException(status_code=500, detail=f"IndexError - There is no data with index {data.id}")
        meme_data = dict(result[0])
        meme_data['file'] = await get_memes_from_minio(meme_data['bucket_name'], meme_data['name'])
    except ValidationError as exc:
        raise HTTPException(status_code=500, detail=f"ValidationError {repr(exc.errors()[0]['type'])}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error {e}")
    return meme_data


@router.get("/memes/{page}/{records}")
async def get_all_memes(page, records):
    """Эндпоинт получения всех мемов с пагинацией"""
    memes_data = list()
    try:
        data = memes.GetMemes(page=page, records=records)
        for obj in await crud.get_meme(page=data.page, records=data.records):
            dict_obj = dict(obj)
            dict_obj['file'] = await get_memes_from_minio(dict_obj['bucket_name'], dict_obj['name'])
            memes_data.append(dict_obj)
    except ValidationError as exc:
        raise HTTPException(status_code=500, detail=f"ValidationError {repr(exc.errors()[0]['type'])}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error {e}")
    return memes_data

