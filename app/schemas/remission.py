from datetime import date

from pydantic import BaseModel


class RemissionItemPropertyBase(BaseModel):
    item_property_id: int
    quantity: int


class RemissionItemPropertyCreate(RemissionItemPropertyBase):
    pass


class RemissionItemPropertyResponse(RemissionItemPropertyBase):
    id: int

    model_config = {"from_attributes": True}


class RemissionItemBase(BaseModel):
    item_id: int
    total_quantity: int


class RemissionItemCreate(RemissionItemBase):
    property_quantities: list[RemissionItemPropertyCreate] | None = []


class RemissionItemResponse(RemissionItemBase):
    id: int
    property_quantities: list[RemissionItemPropertyResponse] = []

    model_config = {"from_attributes": True}


class RemissionBase(BaseModel):
    date: date
    user_associate_id: int


class RemissionCreate(RemissionBase):
    items: list[RemissionItemCreate]


class RemissionUpdate(BaseModel):
    date: date
    status: str | None = None


class RemissionResponse(RemissionBase):
    id: int
    consecutive: int
    status: str
    items: list[RemissionItemResponse] = []

    model_config = {"from_attributes": True}
