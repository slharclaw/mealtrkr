# main.py
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import List

from . import models, schemas, utils, db
from .db import get_db

app = FastAPI(title="Pantry & Refrigerator Inventory Tracker")

# Create DB tables on startup
@app.on_event("startup")
def startup():
    models.Base.metadata.create_all(bind=db.engine)

@app.get("/items", response_model=List[schemas.ItemResponse])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(models.Item).offset(skip).limit(limit).all()
    return items

@app.get("/items/{item_id}", response_model=schemas.ItemResponse)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.post("/items", response_model=schemas.ItemResponse, status_code=201)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    db_item = models.Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.patch("/items/{item_id}", response_model=schemas.ItemResponse)
def update_quantity(item_id: int, update: schemas.ItemUpdate, db: Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    if update.quantity is not None:
        # If unit conversion required
        if update.unit:
            try:
                new_qty = utils.convert(update.quantity, update.unit, db_item.unit)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        else:
            new_qty = update.quantity
        db_item.quantity = new_qty
    elif update.unit:
        # Change unit of the existing quantity
        try:
            new_qty = utils.convert(db_item.quantity, db_item.unit, update.unit)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        db_item.quantity = new_qty
        db_item.unit = update.unit
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return

@app.get("/items/expiring-soon", response_model=List[schemas.ItemResponse])
def expiring_soon(days: int = Query(3, ge=0), db: Session = Depends(get_db)):
    target_date = date.today() + timedelta(days=days)
    items = (
        db.query(models.Item)
        .filter(models.Item.expiration_date != None)
        .filter(models.Item.expiration_date <= target_date)
        .all()
    )
    return items

@app.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    categories = (
        db.query(models.Item.category, db.func.count(models.Item.id))
        .group_by(models.Item.category)
        .all()
    )
    return [{"category": c, "count": cnt} for c, cnt in categories]

if __name__ == "__main__":
    uvicorn.run("pantry_tracker.main:app", host="0.0.0.0", port=8000, reload=True)
