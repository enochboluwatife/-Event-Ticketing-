from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.functions import ST_DWithin
from geoalchemy2.elements import WKTElement
from app.models import Event
from app.repositories.base import BaseRepository

class EventRepository(BaseRepository[Event]):
    def __init__(self, db: AsyncSession):
        super().__init__(Event, db)
    
    async def get_nearby_events(
        self, 
        latitude: float, 
        longitude: float, 
        radius_km: float = 10,
        skip: int = 0,
        limit: int = 100
    ) -> List[Event]:
        """Get events within a certain radius of a location."""
        point = WKTElement(f'POINT({longitude} {latitude})', srid=4326)
        query = (
            select(self.model)
            .where(ST_DWithin(self.model.venue_location, point, radius_km * 1000))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_upcoming_events(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Event]:
        """Get upcoming events sorted by start time."""
        from sqlalchemy import and_, func
        
        query = (
            select(self.model)
            .where(self.model.start_time > func.now())
            .order_by(self.model.start_time)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()