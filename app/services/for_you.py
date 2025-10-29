from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from geoalchemy2 import functions as geofunc
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import Point

from app.models import Event
from app.schemas.event import EventResponse

class ForYouService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_nearby_events(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 10,
        skip: int = 0,
        limit: int = 10
    ) -> List[EventResponse]:
        """
        Get events within a certain radius of a location
        
        Args:
            latitude: Latitude of the center point
            longitude: Longitude of the center point
            radius_km: Radius in kilometers to search within
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of EventResponse objects within the specified radius
        """
        # Convert km to meters (PostGIS uses meters)
        radius_meters = radius_km * 1000
        
        # Create a point from the coordinates
        point = from_shape(Point(longitude, latitude), srid=4326)
        
        # Query events within the radius, ordered by distance
        query = (
            select(Event)
            .where(
                func.ST_DWithin(
                    Event.venue_location,
                    point,
                    radius_meters
                )
            )
            .order_by(
                func.ST_Distance(Event.venue_location, point)
            )
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        events = result.scalars().all()
        
        # Convert to response models
        result_events = []
        for event in events:
            shape = to_shape(event.venue_location)
            result_events.append(
                EventResponse(
                    id=event.id,
                    title=event.title,
                    description=event.description,
                    start_time=event.start_time,
                    end_time=event.end_time,
                    total_tickets=event.total_tickets,
                    tickets_sold=event.tickets_sold,
                    available_tickets=event.total_tickets - event.tickets_sold,
                    venue_address=event.venue_address,
                    venue={
                        "address": event.venue_address,
                        "latitude": shape.y,
                        "longitude": shape.x
                    }
                )
            )
        return result_events

    async def get_recommended_events(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[EventResponse]:
        """
        Get recommended events for a user based on their preferences and history
        
        Args:
            user_id: ID of the user to get recommendations for
            limit: Maximum number of recommendations to return
            
        Returns:
            List of recommended EventResponse objects
        """
        # For now, return upcoming events as recommendations
        # In a real application, this would use a recommendation engine
        query = (
            select(Event)
            .where(Event.start_time >= func.now())
            .order_by(Event.start_time)
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        events = result.scalars().all()
        
        # Convert to response models
        result_events = []
        for event in events:
            shape = to_shape(event.venue_location)
            result_events.append(
                EventResponse(
                    id=event.id,
                    title=event.title,
                    description=event.description,
                    start_time=event.start_time,
                    end_time=event.end_time,
                    total_tickets=event.total_tickets,
                    tickets_sold=event.tickets_sold,
                    available_tickets=event.total_tickets - event.tickets_sold,
                    venue_address=event.venue_address,
                    venue={
                        "address": event.venue_address,
                        "latitude": shape.y,
                        "longitude": shape.x
                    }
                )
            )
        return result_events
