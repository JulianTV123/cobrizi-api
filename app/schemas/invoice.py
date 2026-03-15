from datetime import date

from pydantic import BaseModel


class InvoiceItemBase(BaseModel):
    item_id: int
    quantity: int
    unit_price: float


class InvoiceItemCreate(InvoiceItemBase):
    pass


class InvoiceItemResponse(InvoiceItemBase):
    id: int
    subtotal: float

    model_config = {"from_attributes": True}


class InvoiceBase(BaseModel):
    date: date
    user_associate_id: int


class InvoiceCreate(InvoiceBase):
    items: list[InvoiceItemCreate]


class InvoiceUpdate(BaseModel):
    date: date
    status: str | None = None


class InvoiceResponse(InvoiceBase):
    id: int
    consecutive: int
    total: float
    total_text: str | None = None
    status: str
    items: list[InvoiceItemResponse] = []

    model_config = {"from_attributes": True}
