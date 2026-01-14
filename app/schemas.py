from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class AdvertisementBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    price: float = Field(..., gt=0)
    author: str = Field(..., min_length=1, max_length=50)

class AdvertisementCreate(AdvertisementBase):
    pass

class AdvertisementUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[float] = Field(None, gt=0)
    author: Optional[str] = Field(None, min_length=1, max_length=50)

class AdvertisementOut(AdvertisementBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True