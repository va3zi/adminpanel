from sqlalchemy import Column, String, DateTime, func, Integer, ForeignKey, Numeric, Text, JSON
from sqlalchemy.orm import relationship
from ..db.base import Base

class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), nullable=False, default="IRT") # Assuming Iranian Toman or Rial
    gateway = Column(String(50), nullable=False, default="Zarinpal")
    gateway_transaction_id = Column(String(255), nullable=True, unique=True, index=True) # e.g., Zarinpal Authority or RefID

    # Using String for status, can be an Enum in application layer
    # PENDING, SUCCESSFUL, FAILED, CANCELED
    status = Column(String(50), nullable=False, default="PENDING", index=True)

    description = Column(Text, nullable=True)

    payment_initiated_at = Column(DateTime, default=func.now())
    payment_confirmed_at = Column(DateTime, nullable=True) # When payment is verified successfully

    # Storing raw payloads can be useful for debugging and auditing
    raw_request_payload = Column(JSON, nullable=True)
    raw_response_payload = Column(JSON, nullable=True) # For callback/verification data

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    admin = relationship("Admin", back_populates="payment_transactions")

    def __repr__(self):
        return f"<PaymentTransaction(id={self.id}, admin_id={self.admin_id}, amount={self.amount}, status='{self.status}')>"
