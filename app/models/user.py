from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    id_number = Column(String, nullable=False)
    address = Column(String)
    phone = Column(String)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    associates = relationship(
        "UserAssociate", foreign_keys="UserAssociate.user_id", back_populates="user"
    )
    items = relationship("Item", back_populates="user")
