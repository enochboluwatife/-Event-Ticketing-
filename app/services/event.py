from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import to_shape
from app.models import Event
from app.schemas import EventCreate, EventResponse, VenueSchema
from app.repositories import EventRepository

class EventService:
    def __init__(self, db: AsyncSession):
        self.repository = EventRepository(db)
    
    def _event_to_response(self, event: Event) -> EventResponse:
        """Convert Event model to EventResponse schema."""
        # Extract coordinates from venue_location
        if event.venue_location:
            shape = to_shape(event.venue_location)
            venue = {
                "address": event.venue_address,
                "latitude": shape.y,
                "longitude": shape.x
            }
        else:
            venue = None
        
        return EventResponse(
            id=event.id,
            title=event.title,
            description=event.description,
            start_time=event.start_time,
            end_time=event.end_time,
            total_tickets=event.total_tickets,
            tickets_sold=event.tickets_sold,
            available_tickets=event.available_tickets,
            venue_address=event.venue_address,
            venue=venue
        )
    
    async def create_event(self, event_data: EventCreate) -> EventResponse:
        """Create a new event with venue information."""
        # Create WKT point for venue location (longitude, latitude)
        venue_location = WKTElement(
            f'POINT({event_data.venue.longitude} {event_data.venue.latitude})', 
            srid=4326
        )
        
        event = Event(
            title=event_data.title,
            description=event_data.description,
            start_time=event_data.start_time,
            end_time=event_data.end_time,
            total_tickets=event_data.total_tickets,
            tickets_sold=0,
            venue_address=event_data.venue.address,
            venue_location=venue_location
        )
        
        event = await self.repository.create(event)
        return self._event_to_response(event)
    
    async def get_all_events(self) -> List[EventResponse]:
        """Get all events."""
        events = await self.repository.get_all()
        return [self._event_to_response(event) for event in events]
    
    async def get_event_by_id(self, event_id: int) -> EventResponse:
        """Get event by ID."""
        event = await self.repository.get_by_id(event_id)
        if not event:
            raise ValueError(f"Event with id {event_id} not found")
        return self._event_to_response(event)