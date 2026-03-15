from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db import Base


class RemissionItemProperty(Base):
    __tablename__ = "remission_item_properties"
    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer, nullable=False)
    remission_item_id = Column(
        Integer, ForeignKey("remission_items.id"), nullable=False
    )
    item_property_id = Column(Integer, ForeignKey("item_properties.id"), nullable=False)

    remission_item = relationship("RemissionItem", back_populates="property_quantities")
    item_property = relationship("ItemProperty")
