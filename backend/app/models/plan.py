from sqlalchemy import Column, String, Boolean, DateTime, func, Integer, Numeric
from sqlalchemy.orm import relationship
from ..db.base import Base

class Plan(Base):
    __tablename__ = "plans"

    name = Column(String(100), nullable=False, unique=True)
    duration_days = Column(Integer, nullable=False)
    data_limit_gb = Column(Integer, nullable=False) # In GB
    price = Column(Numeric(10, 2), nullable=False) # Price for the admin to use this plan
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    vpn_users = relationship("VPNUser", back_populates="plan")

    def __repr__(self):
        return f"<Plan(id={self.id}, name='{self.name}', price={self.price})>"
