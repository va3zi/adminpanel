from sqlalchemy import Column, String, DateTime, func, Integer, ForeignKey, Numeric, Boolean, Text
from sqlalchemy.orm import relationship
from ..db.base import Base

class VPNUser(Base):
    __tablename__ = "vpn_users"

    username = Column(String(100), nullable=False, index=True) # Marzban username
    # Password might be managed by Marzban or not stored here directly
    # password_hash = Column(String(255), nullable=True)

    created_by_admin_id = Column(Integer, ForeignKey("admins.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False) # RESTRICT delete by default is fine

    marzban_user_id = Column(String(255), nullable=True, index=True) # Could be the username itself or another ID
    abresani_user_id = Column(String(255), nullable=True, index=True)

    subscription_link = Column(Text, nullable=True)
    qr_code_link = Column(Text, nullable=True) # URL to the QR code image or the data itself

    data_usage_gb = Column(Numeric(10, 2), default=0.0) # In GB
    expires_at = Column(DateTime, nullable=False)

    is_active = Column(Boolean, default=True) # Panel's view of active, Marzban might have its own
    status_notes = Column(Text, nullable=True) # e.g., "Sync pending", "Marzban creation failed"

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    created_by_admin = relationship("Admin", back_populates="vpn_users")
    plan = relationship("Plan", back_populates="vpn_users")
    action_logs = relationship("ActionLog", back_populates="target_user")

    def __repr__(self):
        return f"<VPNUser(id={self.id}, username='{self.username}', admin_id={self.created_by_admin_id})>"
