from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db import get_db
from app.models.item import Item
from app.models.item_property import ItemProperty
from app.models.remission import Remission
from app.models.remission_item import RemissionItem
from app.models.remission_item_property import RemissionItemProperty
from app.models.user import User
from app.models.user_associate import UserAssociate
from app.schemas.remission import RemissionCreate, RemissionResponse, RemissionUpdate
from app.services.email import send_email_with_pdf
from app.services.pdf_remission import generate_remission_pdf

router = APIRouter(prefix="/remissions", tags=["Remissions"])


def get_user_associate_or_404(
    user_associate_id: int, user_id: int, db: Session
) -> UserAssociate:
    link = (
        db.query(UserAssociate)
        .filter(UserAssociate.id == user_associate_id, UserAssociate.user_id == user_id)
        .first()
    )
    if not link:
        raise HTTPException(status_code=404, detail="Relation user-associate not found")
    return link


@router.post("/", response_model=RemissionResponse, status_code=status.HTTP_201_CREATED)
def create_remission(
    data: RemissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    link = get_user_associate_or_404(data.user_associate_id, current_user.id, db)

    link.remission_consecutive += 1
    consecutive = link.remission_consecutive

    remission = Remission(
        consecutive=consecutive,
        date=data.date,
        status="draft",
        user_associate_id=link.id,
    )
    db.add(remission)
    db.flush()

    for i in data.items:
        item = (
            db.query(Item)
            .filter(Item.id == i.item_id, Item.user_id == current_user.id)
            .first()
        )
        if not item:
            raise HTTPException(
                status_code=404, detail=f"Article {i.item_id} not found"
            )

        rem_item = RemissionItem(
            item_id=i.item_id,
            total_quantity=i.total_quantity,
            remission_id=remission.id,
        )
        db.add(rem_item)
        db.flush()

        for prop_qty in i.property_quantities:
            prop = (
                db.query(ItemProperty)
                .filter(
                    ItemProperty.id == prop_qty.item_property_id,
                    ItemProperty.item_id == i.item_id,
                )
                .first()
            )
            if not prop:
                raise HTTPException(
                    status_code=404,
                    detail=f"Property {prop_qty.item_property_id} not found",
                )

            db.add(
                RemissionItemProperty(
                    quantity=prop_qty.quantity,
                    remission_item_id=rem_item.id,
                    item_property_id=prop_qty.item_property_id,
                )
            )

    db.commit()
    db.refresh(remission)
    return remission


@router.get("/", response_model=list[RemissionResponse])
def list_remissions(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    links = (
        db.query(UserAssociate).filter(UserAssociate.user_id == current_user.id).all()
    )
    link_ids = [link.id for link in links]
    return db.query(Remission).filter(Remission.user_associate_id.in_(link_ids)).all()


@router.get("/{remission_id}", response_model=RemissionResponse)
def get_remission(
    remission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    links = (
        db.query(UserAssociate).filter(UserAssociate.user_id == current_user.id).all()
    )
    link_ids = [link.id for link in links]
    remission = (
        db.query(Remission)
        .filter(Remission.id == remission_id, Remission.user_associate_id.in_(link_ids))
        .first()
    )
    if not remission:
        raise HTTPException(status_code=404, detail="Remission not found")
    return remission


@router.put("/{remission_id}", response_model=RemissionResponse)
def update_remission(
    remission_id: int,
    data: RemissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    links = (
        db.query(UserAssociate).filter(UserAssociate.user_id == current_user.id).all()
    )
    link_ids = [link.id for link in links]
    remission = (
        db.query(Remission)
        .filter(Remission.id == remission_id, Remission.user_associate_id.in_(link_ids))
        .first()
    )
    if not remission:
        raise HTTPException(status_code=404, detail="Remission not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(remission, field, value)
    db.commit()
    db.refresh(remission)
    return remission


@router.delete("/{remission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_remission(
    remission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    links = (
        db.query(UserAssociate).filter(UserAssociate.user_id == current_user.id).all()
    )
    link_ids = [link.id for link in links]
    remission = (
        db.query(Remission)
        .filter(Remission.id == remission_id, Remission.user_associate_id.in_(link_ids))
        .first()
    )
    if not remission:
        raise HTTPException(status_code=404, detail="Remission not found")

    db.delete(remission)
    db.commit()


# Download PDF


@router.get("/{remission_id}/pdf")
def download_remission_pdf(
    remission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    links = (
        db.query(UserAssociate).filter(UserAssociate.user_id == current_user.id).all()
    )
    link_ids = [link.id for link in links]
    remission = (
        db.query(Remission)
        .filter(Remission.id == remission_id, Remission.user_associate_id.in_(link_ids))
        .first()
    )
    if not remission:
        raise HTTPException(status_code=404, detail="Remission not found")

    user_associate = remission.user_associate
    associate = user_associate.associate

    pdf_buffer = generate_remission_pdf(remission, current_user, associate)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=remision_{remission.consecutive}.pdf"
        },
    )


# Send PDF via email


@router.post("/{remission_id}/send")
async def send_remission_by_email(
    remission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    links = (
        db.query(UserAssociate).filter(UserAssociate.user_id == current_user.id).all()
    )
    link_ids = [link.id for link in links]
    remission = (
        db.query(Remission)
        .filter(Remission.id == remission_id, Remission.user_associate_id.in_(link_ids))
        .first()
    )
    if not remission:
        raise HTTPException(status_code=404, detail="Remission not found")

    associate = remission.user_associate.associate
    if not associate.email:
        raise HTTPException(
            status_code=400,
            detail="The associate does not have an email address registered",
        )

    pdf_buffer = generate_remission_pdf(remission, current_user, associate)
    filename = f"remision_{remission.consecutive}.pdf"

    await send_email_with_pdf(
        to_email=associate.email,
        subject=f"Remisión N° {remission.consecutive} - {current_user.name}",
        body=f"Estimado/a {associate.name},\n\nAdjunto encontrará la remisión N° {remission.consecutive}.\n\nCordialmente,\n{current_user.name}",
        pdf_buffer=pdf_buffer,
        filename=filename,
    )

    remission.status = "sent"
    db.commit()

    return {"message": f"Remission sent to {associate.email}"}
