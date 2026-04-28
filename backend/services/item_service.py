from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from models import ItemDB


def create(name: str, description: str, db: Session):
    item = ItemDB(name=name, description=description)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_all(db: Session) -> list:
    # Using SQLAlchemy ORM prevents SQL injection
    items = db.query(ItemDB).all()
    return items if items else []


def get_one(item_id: int, db: Session) -> ItemDB:
    if not isinstance(item_id, int) or item_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid item ID")
    item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


def update(item_id: int, name: str, description: str, db: Session):
    item = get_one(item_id, db)
    item.name = name
    item.description = description
    db.commit()
    db.refresh(item)
    return item


def delete(item_id: int, db: Session):
    item = get_one(item_id, db)
    db.delete(item)
    db.commit()
