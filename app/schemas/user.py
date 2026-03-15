from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    name: str
    id_number: str
    address: str | None = None
    phone: str | None = None
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: str | None = None
    id_number: str | None = None
    address: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    password: str | None = None


class UserResponse(UserBase):
    id: int

    model_config = {"from_attributes": True}
