from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db import Base


class RemissionItem(Base):
    __tablename__ = "remission_items"
    id = Column(Integer, primary_key=True, index=True)
    total_quantity = Column(Integer, nullable=False)
    remission_id = Column(Integer, ForeignKey("remissions.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)

    remission = relationship("Remission", back_populates="items")
    item = relationship("Item")
    property_quantities = relationship(
        "RemissionItemProperty", back_populates="remission_item"
    )
