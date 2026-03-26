# models.py
from sqlalchemy import Column, Integer, String, Float, Date, Enum
from .db import Base
import enum

class CategoryEnum(str, enum.Enum):
    pantry = "pantry"
    fridge = "fridge"
    freezer = "freezer"

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    category = Column(Enum(CategoryEnum), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    expiration_date = Column(Date, nullable=True)
