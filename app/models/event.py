from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from geoalchemy2 import Geography
from sqlalchemy.orm import relationship
from app.database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    total_tickets = Column(Integer, nullable=False)
    tickets_sold = Column(Integer, default=0)
    venue_address = Column(String, nullable=False)
    venue_location = Column(Geography(geometry_type='POINT', srid=4326), nullable=False)
    
    # Relationships
    tickets = relationship("Ticket", back_populates="event", cascade="all, delete-orphan")
    
    @property
    def available_tickets(self) -> int:
        return self.total_tickets - self.tickets_sold
    
    def has_available_tickets(self) -> bool:
        return self.available_tickets > 0