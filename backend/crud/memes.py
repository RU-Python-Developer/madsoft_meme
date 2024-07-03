from datetime import datetime

from models.database import database
from models.memes import memes_table as table
from schemas import memes


async def add_meme(data: dict):
    """Добавление записи мема в БД"""
    if not await get_meme(name=data['name']):
        query = table.insert().values(data).returning(table.c.id)
        return await database.execute(query)
    else:
        return False


async def update_meme(data: memes.UpdateMeme, date: datetime):
    """Обновление записи мема в БД"""
    update_data = {val[0]: val[1] for val in data if val[1] and val[0] != 'id'}
    update_data['updated_at'] = date
    meme = await get_meme(id_meme=data.id)

    if meme:
        query = table.update().where(table.c.id == data.id).values(update_data).returning(table.c.id)
        update_meme_id = await database.execute(query)
        if update_meme_id == data.id:
            return meme[0].bucket_name, meme[0].name
        else:
            return False
    else:
        return False


async def get_meme(name: str = None, id_meme: int = None, page: int = None, records: int = None):
    """Получение мемов"""
    query = table.select()
    if page or records:
        query = (table.select()
                 .order_by("id")
                 .offset((page-1) * records)
                 .limit(records))
    if name:
        query = table.select().where(table.c.name == name)
    if id_meme:
        query = table.select().where(table.c.id == id_meme)
    return await database.fetch_all(query)


async def delete_meme(id_meme: int):
    """Удаление записи мема из БД"""
    meme = await get_meme(id_meme=id_meme)
    query = table.delete().where(table.c.id == id_meme).returning(table.c.name)
    res = await database.execute(query)
    if meme and meme[0].name == res:
        return meme[0].bucket_name, meme[0].name
    else:
        return False
