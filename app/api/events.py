from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.event import EventCreate, EventResponse, EventUpdate
from app.services.event import EventService

router = APIRouter()

@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new event"""
    event_service = EventService(db)
    try:
        event = await event_service.create_event(event_data)
        return event
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[EventResponse])
async def list_events(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all events with pagination"""
    event_service = EventService(db)
    events = await event_service.get_all_events()
    return events[skip : skip + limit]

@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get event by ID"""
    event_service = EventService(db)
    try:
        event = await event_service.get_event_by_id(event_id)
        return event
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )