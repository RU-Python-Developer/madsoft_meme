import uvicorn
from fastapi import FastAPI
from models.database import database
from fastapi.middleware.cors import CORSMiddleware

from routers import memes_public, memes_private
from settings.config import settings as config


app = FastAPI()

origins = config.HOST

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


app.include_router(tags=["public_memes"], router=memes_public.router)
app.include_router(tags=["private_memes"], router=memes_private.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
