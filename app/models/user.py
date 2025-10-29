from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
from app.database import Base
from datetime import datetime, timezone


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # User location for geospatial queries (latitude, longitude)
    location = Column(Geography(geometry_type='POINT', srid=4326), nullable=True)
    
    # Authentication fields
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tickets = relationship("Ticket", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"