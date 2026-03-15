from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db import get_db
from app.models.item import Item
from app.models.item_property import ItemProperty
from app.models.user import User
from app.schemas.item import (
    ItemCreate,
    ItemPropertyCreate,
    ItemPropertyResponse,
    ItemResponse,
    ItemUpdate,
)

router = APIRouter(prefix="/items", tags=["Items"])


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    data: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = Item(name=data.name, description=data.description, user_id=current_user.id)
    db.add(item)
    db.flush()

    for prop in data.properties:
        db.add(ItemProperty(name=prop.name, item_id=item.id))

    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=list[ItemResponse])
def list_items(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return db.query(Item).filter(Item.user_id == current_user.id).all()


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = (
        db.query(Item)
        .filter(Item.id == item_id, Item.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.put("/{item_id}", response_model=ItemResponse)
def update_item(
    item_id: int,
    data: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = (
        db.query(Item)
        .filter(Item.id == item_id, Item.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = (
        db.query(Item)
        .filter(Item.id == item_id, Item.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()


# Item Properties endpoints


@router.post(
    "/{item_id}/properties",
    response_model=ItemPropertyResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_property(
    item_id: int,
    data: ItemPropertyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = (
        db.query(Item)
        .filter(Item.id == item_id, Item.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    prop = ItemProperty(name=data.name, item_id=item_id)
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return prop


@router.delete(
    "/{item_id}/properties/{property_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_property(
    item_id: int,
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = (
        db.query(Item)
        .filter(Item.id == item_id, Item.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    prop = (
        db.query(ItemProperty)
        .filter(ItemProperty.id == property_id, ItemProperty.item_id == item_id)
        .first()
    )
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    db.delete(prop)
    db.commit()
