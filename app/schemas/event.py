from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Union, Dict, Any

class VenueSchema(BaseModel):
    address: str = Field(..., description="Physical address of the venue")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate of the venue")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate of the venue")

class EventBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    start_time: datetime
    end_time: datetime
    total_tickets: int = Field(..., gt=0, description="Total number of available tickets")
    venue: VenueSchema

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_tickets: Optional[int] = Field(None, gt=0, description="Total number of available tickets")
    venue: Optional[VenueSchema] = None

class EventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    total_tickets: int
    tickets_sold: int
    available_tickets: int
    venue_address: str
    venue: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            'datetime': lambda v: v.isoformat()
        }
    )