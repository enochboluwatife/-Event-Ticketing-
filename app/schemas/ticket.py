from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Any

class TicketBase(BaseModel):
    user_id: int
    event_id: int

class TicketCreate(TicketBase):
    pass

class TicketPayment(BaseModel):
    payment_reference: str = Field(..., min_length=1, description="Unique payment reference ID")
    paid_at: Optional[datetime] = None

class TicketResponse(TicketBase):
    id: int
    status: str
    created_at: datetime
    payment_reference: Optional[str] = None
    paid_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            'datetime': lambda v: v.isoformat()
        }
    )