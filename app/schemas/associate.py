from pydantic import BaseModel, EmailStr


class AssociateBase(BaseModel):
    name: str
    id_number: str | None = None
    address: str | None = None
    email: EmailStr | None = None
    user_id: int | None = None


class AssociateCreate(AssociateBase):
    pass


class AssociateUpdate(BaseModel):
    name: str | None = None
    id_number: str | None = None
    address: str | None = None
    email: EmailStr | None = None


class AssociateResponse(AssociateBase):
    id: int

    model_config = {"from_attributes": True}
