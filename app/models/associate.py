from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base


class Associate(Base):
    __tablename__ = "associates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    id_number = Column(String)
    address = Column(String)
    email = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    linked_user = relationship("User", foreign_keys=[user_id])
