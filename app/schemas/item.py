from pydantic import BaseModel


class ItemPropertyBase(BaseModel):
    name: str


class ItemPropertyCreate(ItemPropertyBase):
    pass


class ItemPropertyResponse(ItemPropertyBase):
    id: int

    model_config = {"from_attributes": True}


class ItemBase(BaseModel):
    name: str
    description: str | None = None


class ItemCreate(ItemBase):
    properties: list[ItemPropertyCreate] | None = []


class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ItemResponse(ItemBase):
    id: int
    user_id: int
    properties: list[ItemPropertyResponse] = []

    model_config = {"from_attributes": True}
