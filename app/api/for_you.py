from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.event import EventResponse
from app.services.for_you import ForYouService

router = APIRouter()

@router.get("/events/nearby", response_model=List[EventResponse])
async def get_nearby_events(
    latitude: float,
    longitude: float,
    radius_km: float = 10,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get events near a specific location"""
    for_you_service = ForYouService(db)
    try:
        events = await for_you_service.get_nearby_events(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            skip=skip,
            limit=limit
        )
        return events
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/events/recommended", response_model=List[EventResponse])
async def get_recommended_events(
    user_id: int,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get recommended events for a user"""
    for_you_service = ForYouService(db)
    try:
        events = await for_you_service.get_recommended_events(
            user_id=user_id,
            limit=limit
        )
        return events
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )