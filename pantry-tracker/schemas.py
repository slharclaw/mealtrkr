# schemas.py
from pydantic import BaseModel, Field, validator
from datetime import date
from typing import Optional
from enum import Enum

class Category(str, Enum):
    pantry = "pantry"
    fridge = "fridge"
    freezer = "freezer"

class ItemBase(BaseModel):
    name: str = Field(..., example="Milk")
    category: Category = Field(..., example="fridge")
    quantity: float = Field(..., gt=0, example=1.0)
    unit: str = Field(..., example="L")
    expiration_date: Optional[date] = Field(None, example="2026-04-01")

    @validator('expiration_date')
    def check_future(cls, v):
        if v is not None and v <= date.today():
            raise ValueError('expiration_date must be in the future')
        return v

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    quantity: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = None

    @validator('quantity')
    def quantity_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('quantity must be positive')
        return v

class ItemResponse(ItemBase):
    id: int

    class Config:
        orm_mode = True
