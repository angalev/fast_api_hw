from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(title="Advertisement Service")

# Временная "база данных"
database = {}
next_id = 1


# Модель объявления
class Advertisement(BaseModel):
    title: str
    description: str
    price: float
    author: str
    created_at: datetime = None

    def model_post_init(self, __context):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)


# Модель ответа с id
class AdvertisementOut(Advertisement):
    id: int


# Модель для частичного обновления
class AdvertisementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    author: Optional[str] = None


# POST /advertisement — создание
@app.post("/advertisement", response_model=AdvertisementOut)
def create_ad(ad: Advertisement):
    global next_id
    ad_out = AdvertisementOut(**ad.model_dump(), id=next_id)
    database[next_id] = ad_out
    next_id += 1
    return ad_out


# GET /advertisement/{advertisement_id}
@app.get("/advertisement/{advertisement_id}", response_model=AdvertisementOut)
def get_ad(advertisement_id: int):
    ad = database.get(advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return ad


# PATCH /advertisement/{advertisement_id} — обновление
@app.patch("/advertisement/{advertisement_id}", response_model=AdvertisementOut)
def update_ad(advertisement_id: int, ad_update: AdvertisementUpdate):
    ad = database.get(advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")

    update_data = ad_update.model_dump(exclude_unset=True)
    updated_ad = ad.model_copy(update=update_data)
    database[advertisement_id] = updated_ad
    return updated_ad


# DELETE /advertisement/{advertisement_id}
@app.delete("/advertisement/{advertisement_id}")
def delete_ad(advertisement_id: int):
    ad = database.get(advertisement_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    del database[advertisement_id]
    return {"status": "deleted"}


# GET /advertisement — поиск по полям
@app.get("/advertisement", response_model=List[AdvertisementOut])
def search_ads(
    title: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None)
):
    results = list(database.values())
    if title:
        results = [ad for ad in results if title.lower() in ad.title.lower()]
    if author:
        results = [ad for ad in results if author.lower() in ad.author.lower()]
    if min_price is not None:
        results = [ad for ad in results if ad.price >= min_price]
    if max_price is not None:
        results = [ad for ad in results if ad.price <= max_price]
    return results


# Опционально: проверка работы
@app.get("/")
def root():
    return {"message": "Advertisement Service is running"}