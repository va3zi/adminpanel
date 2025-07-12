from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func # For server-side default timestamp
from .database import Base

class SuperAdmin(Base):
    __tablename__ = "super_admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    balance = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_by_super_admin_id = Column(Integer, ForeignKey("super_admins.id")) # Optional: link to creating super_admin
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    # created_by = relationship("SuperAdmin") # If you want to access the SuperAdmin object
    # vpn_users = relationship("VpnUser", back_populates="owner_admin")
    # payment_logs = relationship("PaymentLog", back_populates="admin")


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    price = Column(Float, nullable=False) # Price in IRR (or preferred currency)
    duration_days = Column(Integer, nullable=False) # Duration in days
    data_limit_gb = Column(Float, nullable=False) # Data limit in GB
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Future models (will be uncommented/added in later steps)
# class VpnUser(Base):
#     __tablename__ = "vpn_users"
#     id = Column(Integer, primary_key=True, index=True)
#     admin_id = Column(Integer, ForeignKey("admins.id"))
#     plan_id = Column(Integer, ForeignKey("plans.id"))
#     marzban_user_id = Column(String, unique=True, index=True, nullable=True) # ID from Marzban
#     abresani_user_id = Column(String, unique=True, index=True, nullable=True) # ID from Abresani
#     username = Column(String, unique=True, index=True) # May be generated or from Marzban
#     # ... other user details, status, expiry, etc.
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     updated_at = Column(DateTime(timezone=True), onupdate=func.now())
#
#     owner_admin = relationship("Admin", back_populates="vpn_users")
#     plan = relationship("Plan")

# class PaymentLog(Base):
#     __tablename__ = "payment_logs"
#     id = Column(Integer, primary_key=True, index=True)
#     admin_id = Column(Integer, ForeignKey("admins.id"))
#     amount = Column(Float, nullable=False)
#     transaction_id = Column(String, unique=True, index=True) # Zarinpal transaction ID
#     status = Column(String) # e.g., 'pending', 'completed', 'failed'
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     verified_at = Column(DateTime(timezone=True), nullable=True)
#
#     admin = relationship("Admin", back_populates="payment_logs")

# To create tables in the database, you'd typically use Alembic or a similar migration tool,
# or for simple cases: Base.metadata.create_all(bind=engine)
# This line should be called cautiously, ideally managed by a migration system in a real app.
# For now, we'll call it once in main.py for initial setup for simplicity.
