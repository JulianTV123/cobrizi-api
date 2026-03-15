from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base


class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    consecutive = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    total = Column(Float, nullable=False)
    total_text = Column(String)
    status = Column(String, default="draft")
    user_associate_id = Column(
        Integer, ForeignKey("user_associates.id"), nullable=False
    )

    user_associate = relationship("UserAssociate", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice")
