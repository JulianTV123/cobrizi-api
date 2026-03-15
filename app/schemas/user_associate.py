from pydantic import BaseModel


class UserAssociateCreate(BaseModel):
    associate_id: int


class UserAssociateResponse(BaseModel):
    id: int
    user_id: int
    associate_id: int
    invoice_consecutive: int
    remission_consecutive: int

    model_config = {"from_attributes": True}
