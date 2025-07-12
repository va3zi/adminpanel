from sqlalchemy import Column, String, DateTime, func, Integer, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from ..db.base import Base

class ActionLog(Base):
    __tablename__ = "action_logs"

    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=True)
    super_admin_id = Column(Integer, ForeignKey("super_admins.id"), nullable=True)
    target_user_id = Column(Integer, ForeignKey("vpn_users.id"), nullable=True) # If action relates to a VPN user

    action_type = Column(String(100), nullable=False, index=True)
    # e.g., 'ADMIN_LOGIN_SUCCESS', 'ADMIN_LOGIN_FAILURE',
    # 'SUPER_ADMIN_CREATE_ADMIN', 'ADMIN_CREATE_VPN_USER',
    # 'ADMIN_DELETE_VPN_USER', 'ADMIN_RECHARGE_INITIATED', 'ADMIN_RECHARGE_SUCCESS'

    details = Column(JSON, nullable=True) # Store relevant data, e.g., { 'amount': 10000 } for recharge
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=func.now(), index=True)

    # Relationships
    admin = relationship("Admin", back_populates="action_logs")
    super_admin = relationship("SuperAdmin", back_populates="action_logs")
    target_user = relationship("VPNUser", back_populates="action_logs")

    def __repr__(self):
        actor = ""
        if self.admin_id:
            actor = f"admin_id={self.admin_id}"
        elif self.super_admin_id:
            actor = f"super_admin_id={self.super_admin_id}"
        return f"<ActionLog(id={self.id}, type='{self.action_type}', {actor}, target_user_id={self.target_user_id})>"
