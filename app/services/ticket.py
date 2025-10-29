from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timezone, timedelta
from app.models import Ticket, Event
from app.repositories.base import BaseRepository
from typing import Optional, List

class TicketService(BaseRepository[Ticket]):
    def __init__(self, db: AsyncSession):
        super().__init__(Ticket, db)

    async def create_ticket(self, ticket_data) -> Ticket:
        """Create a new ticket with status 'reserved'"""
        # Check if event exists and has available tickets
        result = await self.db.execute(
            select(Event)
            .where(Event.id == ticket_data.event_id)
            .with_for_update()
        )
        event = result.scalar_one_or_none()
        
        if not event:
            raise ValueError("Event not found")
        
        if event.tickets_sold >= event.total_tickets:
            raise ValueError("No tickets available for this event")
        
        # Create the ticket
        ticket = Ticket(
            user_id=ticket_data.user_id,
            event_id=ticket_data.event_id,
            status='reserved',
            created_at=datetime.now(timezone.utc)
        )
        
        # Update tickets count
        event.tickets_sold += 1
        
        self.db.add(ticket)
        await self.db.commit()
        await self.db.refresh(ticket)
        
        return ticket

    async def pay_ticket(self, ticket_id: int, payment_reference: str, paid_at: datetime) -> Ticket:
        """Mark a ticket as paid"""
        result = await self.db.execute(
            select(Ticket)
            .where(Ticket.id == ticket_id)
            .with_for_update()
        )
        ticket = result.scalar_one_or_none()
        
        if not ticket:
            raise ValueError("Ticket not found")
        
        if ticket.status != 'reserved':
            raise ValueError(f"Cannot pay for ticket with status: {ticket.status}")
        
        ticket.status = 'paid'
        ticket.payment_reference = payment_reference
        ticket.paid_at = paid_at
        
        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket

    async def get_ticket_by_id(self, ticket_id: int) -> Optional[Ticket]:
        """Get a ticket by its ID"""
        result = await self.db.execute(
            select(Ticket)
            .where(Ticket.id == ticket_id)
        )
        return result.scalar_one_or_none()

    async def get_tickets_by_user(self, user_id: int) -> List[Ticket]:
        """Get all tickets for a user"""
        result = await self.db.execute(
            select(Ticket)
            .where(Ticket.user_id == user_id)
            .order_by(Ticket.created_at.desc())
        )
        return result.scalars().all()
    
    async def expire_old_tickets(self) -> int:
        """Expire tickets that haven't been paid for"""
        result = await self.db.execute(
            select(Ticket)
            .where(
                and_(
                    Ticket.status == 'reserved',
                    Ticket.created_at < datetime.now(timezone.utc) - timedelta(minutes=2)
                )
            )
            .with_for_update()
        )
        
        tickets = result.scalars().all()
        expired_count = 0
        
        for ticket in tickets:
            # Get the associated event to update available tickets
            event_result = await self.db.execute(
                select(Event)
                .where(Event.id == ticket.event_id)
                .with_for_update()
            )
            event = event_result.scalar_one_or_none()
            
            if event:
                event.tickets_sold -= 1
            
            ticket.status = 'expired'
            expired_count += 1
        
        if expired_count > 0:
            await self.db.commit()
        
        return expired_count