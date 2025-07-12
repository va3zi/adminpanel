from sqlalchemy import Column, String, Boolean, DateTime, func, ForeignKey, Numeric, Integer
from sqlalchemy.orm import relationship
from ..db.base import Base

class Admin(Base):
    __tablename__ = "admins"

    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    balance = Column(Numeric(10, 2), nullable=False, default=0.00)
    is_active = Column(Boolean, default=True)

    created_by_super_admin_id = Column(Integer, ForeignKey("super_admins.id"), nullable=True)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    created_by_super_admin = relationship("SuperAdmin", back_populates="created_admins")
    vpn_users = relationship("VPNUser", back_populates="created_by_admin", cascade="all, delete-orphan")
    payment_transactions = relationship("PaymentTransaction", back_populates="admin", cascade="all, delete-orphan")
    action_logs = relationship("ActionLog", back_populates="admin")

    def __repr__(self):
        return f"<Admin(id={self.id}, username='{self.username}', balance={self.balance})>"
