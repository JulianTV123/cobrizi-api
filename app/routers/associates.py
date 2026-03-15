from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db import get_db
from app.models.associate import Associate
from app.models.user import User
from app.models.user_associate import UserAssociate
from app.schemas.associate import AssociateCreate, AssociateResponse, AssociateUpdate

router = APIRouter(prefix="/associates", tags=["Associates"])


@router.post("/", response_model=AssociateResponse, status_code=status.HTTP_201_CREATED)
def create_associate(
    data: AssociateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    associate = Associate(**data.model_dump())
    db.add(associate)
    db.flush()

    link = UserAssociate(user_id=current_user.id, associate_id=associate.id)
    db.add(link)
    db.commit()
    db.refresh(associate)
    return associate


@router.get("/", response_model=list[AssociateResponse])
def list_my_associates(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    links = (
        db.query(UserAssociate).filter(UserAssociate.user_id == current_user.id).all()
    )
    return [link.associate for link in links]


@router.get("/{associate_id}", response_model=AssociateResponse)
def get_associate(
    associate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    link = (
        db.query(UserAssociate)
        .filter(
            UserAssociate.user_id == current_user.id,
            UserAssociate.associate_id == associate_id,
        )
        .first()
    )
    if not link:
        raise HTTPException(status_code=404, detail="Associate not found")
    return link.associate


@router.put("/{associate_id}", response_model=AssociateResponse)
def update_associate(
    associate_id: int,
    data: AssociateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    link = (
        db.query(UserAssociate)
        .filter(
            UserAssociate.user_id == current_user.id,
            UserAssociate.associate_id == associate_id,
        )
        .first()
    )
    if not link:
        raise HTTPException(status_code=404, detail="Associate not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(link.associate, field, value)
    db.commit()
    db.refresh(link.associate)
    return link.associate


@router.delete("/{associate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_associate(
    associate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    link = (
        db.query(UserAssociate)
        .filter(
            UserAssociate.user_id == current_user.id,
            UserAssociate.associate_id == associate_id,
        )
        .first()
    )
    if not link:
        raise HTTPException(status_code=404, detail="Associate not found")

    db.delete(link)
    db.delete(link.associate)
    db.commit()
