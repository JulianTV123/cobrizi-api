from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db import Base


class UserAssociate(Base):
    __tablename__ = "user_associates"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    associate_id = Column(Integer, ForeignKey("associates.id"), nullable=False)
    invoice_consecutive = Column(Integer, default=0)
    remission_consecutive = Column(Integer, default=0)

    user = relationship("User", foreign_keys=[user_id], back_populates="associates")
    associate = relationship("Associate", foreign_keys=[associate_id])
    invoices = relationship("Invoice", back_populates="user_associate")
    remissions = relationship("Remission", back_populates="user_associate")
