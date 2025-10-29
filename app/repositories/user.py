from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email address."""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_users_near_location(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 10,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get users within a certain radius of a location."""
        from geoalchemy2.functions import ST_DWithin
        from geoalchemy2.elements import WKTElement
        
        point = WKTElement(f'POINT({longitude} {latitude})', srid=4326)
        query = (
            select(User)
            .where(
                User.location.isnot(None),
                ST_DWithin(User.location, point, radius_km * 1000)
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_user_tickets(self, user_id: int) -> List[dict]:
        """Get all tickets for a user with event details."""
        from sqlalchemy.orm import selectinload
        from app.models.ticket import Ticket
        
        result = await self.db.execute(
            select(Ticket)
            .where(Ticket.user_id == user_id)
            .options(
                selectinload(Ticket.event)
            )
            .order_by(Ticket.created_at.desc())
        )
        
        tickets = result.scalars().all()
        return [
            {
                'id': ticket.id,
                'status': ticket.status.value,
                'created_at': ticket.created_at,
                'event': {
                    'id': ticket.event.id,
                    'title': ticket.event.title,
                    'start_time': ticket.event.start_time,
                    'venue_address': ticket.event.venue_address
                }
            }
            for ticket in tickets
        ]