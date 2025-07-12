from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.orm import relationship
from ..db.base import Base

class SuperAdmin(Base):
    __tablename__ = "super_admins"  # Explicitly defining for clarity, though Base would generate it

    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    created_admins = relationship("Admin", back_populates="created_by_super_admin")
    action_logs = relationship("ActionLog", back_populates="super_admin")

    def __repr__(self):
        return f"<SuperAdmin(id={self.id}, username='{self.username}')>"
