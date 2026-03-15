from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base


class ItemProperty(Base):
    __tablename__ = "item_properties"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)

    item = relationship("Item", back_populates="properties")
