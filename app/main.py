from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app import schemas, crud
from app.database import engine, get_db
from app.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Действия при запуске приложения
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Advertisement Service",
    description="API for managing advertisements with PostgreSQL, SQLAlchemy, and async support.",
    version="1.0.0",
    lifespan=lifespan
)


@app.post("/advertisement", response_model=schemas.AdvertisementOut)
async def create_ad(ad: schemas.AdvertisementCreate, db: AsyncSession = Depends(get_db)):
    """
    Создать новое объявление
    """
    db_ad = await crud.create_ad(db, ad)
    return db_ad


@app.get("/advertisement/{advertisement_id}", response_model=schemas.AdvertisementOut)
async def get_ad(advertisement_id: int, db: AsyncSession = Depends(get_db)):
    """
    Получить объявление по ID
    """
    ad = await crud.get_ad(db, advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return ad


@app.patch("/advertisement/{advertisement_id}", response_model=schemas.AdvertisementOut)
async def update_ad(
    advertisement_id: int,
    ad_update: schemas.AdvertisementUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Частично обновить объявление
    """
    ad = await crud.update_ad(db, advertisement_id, ad_update)
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return ad


@app.delete("/advertisement/{advertisement_id}")
async def delete_ad(advertisement_id: int, db: AsyncSession = Depends(get_db)):
    """
    Удалить объявление
    """
    success = await crud.delete_ad(db, advertisement_id)
    if not success:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return {"status": "deleted"}


@app.get("/advertisement", response_model=List[schemas.AdvertisementOut])
async def search_ads(
    title: Optional[str] = Query(None, description="Поиск по заголовку (частичное совпадение)"),
    description: Optional[str] = Query(None, description="Поиск по описанию (частичное)"),
    author: Optional[str] = Query(None, description="Поиск по автору"),
    price: Optional[float] = Query(None, ge=0, description="Точная цена"),
    min_price: Optional[float] = Query(None, ge=0, description="Минимальная цена"),
    max_price: Optional[float] = Query(None, ge=0, description="Максимальная цена"),
    limit: int = Query(100, ge=1, le=1000, description="Количество результатов"),
    offset: int = Query(0, ge=0, description="Смещение для пагинации"),
    db: AsyncSession = Depends(get_db)
):
    """
    Поиск объявлений с фильтрацией и пагинацией
    """
    ads = await crud.search_ads(
        db, title, description, author, price, min_price, max_price, limit, offset
    )
    return ads


@app.get("/")
def root():
    """
    Проверка работоспособности
    """
    return {"message": "Advertisement Service is running"}