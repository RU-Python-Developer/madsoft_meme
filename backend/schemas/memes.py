import json

from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from settings.config import settings


# Public
class GetMeme(BaseModel):
    id: int


class GetMemes(BaseModel):
    page: int | None
    records: int | None


# Private
class UploadMemes(BaseModel):
    bucket_name: str
    description: str


class UpdateMeme(BaseModel):
    """Схема данных обновления записи"""

    id: int
    description: str | None

    def set_attr(self, key: str, val: str):
        self.__dict__[key] = val


class DeleteMeme(BaseModel):
    id: int


class UserBase(BaseModel):
    # username: str
    name: str | None = None


class Token(BaseModel):
    access_token: str | bool = False
    token_type: str


class TokenData(BaseModel):
    log: str | None = None
