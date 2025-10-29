from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class UserResponse(UserBase):
    id: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    class Config:
        from_attributes = True