from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class TicketStatus(str, enum.Enum):
    RESERVED = "reserved"
    PAID = "paid"
    EXPIRED = "expired"

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(TicketStatus), default=TicketStatus.RESERVED, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    payment_reference = Column(String, nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="tickets")
    event = relationship("Event", back_populates="tickets")
    
    @property
    def is_expired(self) -> bool:
        """Check if the ticket has expired"""
        if self.status == TicketStatus.PAID:
            return False
            
        time_since_creation = datetime.utcnow() - self.created_at
        return time_since_creation.total_seconds() > 120  # 2 minutes in seconds
    
    def mark_as_paid(self, payment_reference: str) -> None:
        """Mark the ticket as paid"""
        self.status = TicketStatus.PAID
        self.payment_reference = payment_reference
        self.paid_at = datetime.utcnow()
    
    def mark_as_expired(self) -> None:
        """Mark the ticket as expired"""
        if self.status != TicketStatus.PAID:  # Only expire if not already paid
            self.status = TicketStatus.EXPIRED