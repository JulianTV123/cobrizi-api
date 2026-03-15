from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from num2words import num2words
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db import get_db
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.models.item import Item
from app.models.user import User
from app.models.user_associate import UserAssociate
from app.schemas.invoice import InvoiceCreate, InvoiceResponse, InvoiceUpdate
from app.services.email import send_email_with_pdf
from app.services.pdf_invoice import generate_invoice_pdf

router = APIRouter(prefix="/invoices", tags=["Invoices"])


def total_to_text(total: float) -> str:
    integer_part = int(total)
    text = num2words(integer_part, lang="es").capitalize()
    return f"{text} pesos"


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


@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    link = get_user_associate_or_404(data.user_associate_id, current_user.id, db)

    link.invoice_consecutive += 1
    consecutive = link.invoice_consecutive

    total = 0.0
    invoice_items = []
    for i in data.items:
        item = (
            db.query(Item)
            .filter(Item.id == i.item_id, Item.user_id == current_user.id)
            .first()
        )
        if not item:
            raise HTTPException(status_code=404, detail=f"Item {i.item_id} not found")
        subtotal = i.quantity * i.unit_price
        total += subtotal
        invoice_items.append(
            InvoiceItem(
                item_id=i.item_id,
                quantity=i.quantity,
                unit_price=i.unit_price,
                subtotal=subtotal,
            )
        )

    invoice = Invoice(
        consecutive=consecutive,
        date=data.date,
        total=total,
        total_text=total_to_text(total),
        status="draft",
        user_associate_id=link.id,
    )
    db.add(invoice)
    db.flush()

    for inv_item in invoice_items:
        inv_item.invoice_id = invoice.id
        db.add(inv_item)

    db.commit()
    db.refresh(invoice)
    return invoice


@router.get("/", response_model=list[InvoiceResponse])
def list_invoices(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    links = (
        db.query(UserAssociate).filter(UserAssociate.user_id == current_user.id).all()
    )
    link_ids = [link.id for link in links]
    return db.query(Invoice).filter(Invoice.user_associate_id.in_(link_ids)).all()


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    links = (
        db.query(UserAssociate).filter(UserAssociate.user_id == current_user.id).all()
    )
    link_ids = [link.id for link in links]
    invoice = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id, Invoice.user_associate_id.in_(link_ids))
        .first()
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="Account of collection not found")
    return invoice


@router.put("/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(
    invoice_id: int,
    data: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    links = (
        db.query(UserAssociate).filter(UserAssociate.user_id == current_user.id).all()
    )
    link_ids = [link.id for link in links]
    invoice = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id, Invoice.user_associate_id.in_(link_ids))
        .first()
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="Account of collection not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(invoice, field, value)
    db.commit()
    db.refresh(invoice)
    return invoice


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    links = (
        db.query(UserAssociate).filter(UserAssociate.user_id == current_user.id).all()
    )
    link_ids = [link.id for link in links]
    invoice = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id, Invoice.user_associate_id.in_(link_ids))
        .first()
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="Account of collection not found")

    db.delete(invoice)
    db.commit()


# Download PDF


@router.get("/{invoice_id}/pdf")
def download_invoice_pdf(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    links = (
        db.query(UserAssociate).filter(UserAssociate.user_id == current_user.id).all()
    )
    link_ids = [link.id for link in links]
    invoice = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id, Invoice.user_associate_id.in_(link_ids))
        .first()
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="Account of collection not found")

    user_associate = invoice.user_associate
    associate = user_associate.associate

    pdf_buffer = generate_invoice_pdf(invoice, current_user, associate)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=cuenta_cobro_{invoice.consecutive}.pdf"
        },
    )


# Send PDF via email


@router.post("/{invoice_id}/send")
async def send_invoice_by_email(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    links = (
        db.query(UserAssociate).filter(UserAssociate.user_id == current_user.id).all()
    )
    link_ids = [link.id for link in links]
    invoice = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id, Invoice.user_associate_id.in_(link_ids))
        .first()
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="Account of collection not found")

    associate = invoice.user_associate.associate
    if not associate.email:
        raise HTTPException(
            status_code=400,
            detail="This associate does not have an email address registered",
        )

    pdf_buffer = generate_invoice_pdf(invoice, current_user, associate)
    filename = f"cuenta_cobro_{invoice.consecutive}.pdf"

    await send_email_with_pdf(
        to_email=associate.email,
        subject=f"Cuenta de Cobro N° {invoice.consecutive} - {current_user.name}",
        body=f"Estimado/a {associate.name},\n\nAdjunto encontrará la cuenta de cobro N° {invoice.consecutive} por valor de ${invoice.total:,.0f}.\n\nCordialmente,\n{current_user.name}",
        pdf_buffer=pdf_buffer,
        filename=filename,
    )

    invoice.status = "sent"
    db.commit()

    return {"message": f"Account of collection sent to {associate.email}"}
