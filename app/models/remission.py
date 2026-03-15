from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base


class Remission(Base):
    __tablename__ = "remissions"
    id = Column(Integer, primary_key=True, index=True)
    consecutive = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String, default="draft")
    user_associate_id = Column(
        Integer, ForeignKey("user_associates.id"), nullable=False
    )

    user_associate = relationship("UserAssociate", back_populates="remissions")
    items = relationship("RemissionItem", back_populates="remission")
