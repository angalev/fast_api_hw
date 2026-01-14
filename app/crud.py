from sqlalchemy.future import select
from app.models import AdvertisementDB
from app.schemas import AdvertisementCreate, AdvertisementUpdate
from sqlalchemy.ext.asyncio import AsyncSession

async def create_ad(db: AsyncSession, ad: AdvertisementCreate):
    db_ad = AdvertisementDB(**ad.model_dump())
    db.add(db_ad)
    await db.commit()
    await db.refresh(db_ad)
    return db_ad

async def get_ad(db: AsyncSession, ad_id: int):
    result = await db.execute(select(AdvertisementDB).where(AdvertisementDB.id == ad_id))
    return result.scalar_one_or_none()

async def update_ad(db: AsyncSession, ad_id: int, ad_update: AdvertisementUpdate):
    db_ad = await get_ad(db, ad_id)
    if not db_ad:
        return None
    update_data = ad_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_ad, key, value)
    await db.commit()
    await db.refresh(db_ad)
    return db_ad

async def delete_ad(db: AsyncSession, ad_id: int):
    db_ad = await get_ad(db, ad_id)
    if not db_ad:
        return False
    await db.delete(db_ad)
    await db.commit()
    return True

async def search_ads(
    db: AsyncSession,
    title: str = None,
    description: str = None,
    author: str = None,
    price: float = None,
    min_price: float = None,
    max_price: float = None,
    limit: int = 100,
    offset: int = 0
):
    query = select(AdvertisementDB)

    if title:
        query = query.where(AdvertisementDB.title.ilike(f"%{title}%"))
    if description:
        query = query.where(AdvertisementDB.description.ilike(f"%{description}%"))
    if author:
        query = query.where(AdvertisementDB.author.ilike(f"%{author}%"))
    if price is not None:
        query = query.where(AdvertisementDB.price == price)
    if min_price is not None:
        query = query.where(AdvertisementDB.price >= min_price)
    if max_price is not None:
        query = query.where(AdvertisementDB.price <= max_price)

    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()