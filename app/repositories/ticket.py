from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta

from app.models.ticket import Ticket, TicketStatus
from app.repositories.base import BaseRepository

class TicketRepository(BaseRepository[Ticket]):
    def __init__(self, db: AsyncSession):
        super().__init__(Ticket, db)

    async def get_by_id(self, ticket_id: int) -> Optional[Ticket]:
        """Get a ticket by ID"""
        result = await self.db.execute(
            select(Ticket)
            .where(Ticket.id == ticket_id)
            .options(
                # Eager load relationships
                selectinload(Ticket.user),
                selectinload(Ticket.event)
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: int) -> List[Ticket]:
        """Get all tickets for a specific user"""
        result = await self.db.execute(
            select(Ticket)
            .where(Ticket.user_id == user_id)
            .order_by(Ticket.created_at.desc())
            .options(
                selectinload(Ticket.event)
            )
        )
        return result.scalars().all()

    async def get_by_event(self, event_id: int) -> List[Ticket]:
        """Get all tickets for a specific event"""
        result = await self.db.execute(
            select(Ticket)
            .where(Ticket.event_id == event_id)
            .options(
                selectinload(Ticket.user)
            )
        )
        return result.scalars().all()

    async def get_expired_tickets(self) -> List[Ticket]:
        """Get all reserved tickets that have expired"""
        expiration_time = datetime.utcnow() - timedelta(minutes=2)
        
        result = await self.db.execute(
            select(Ticket)
            .where(
                and_(
                    Ticket.status == TicketStatus.RESERVED,
                    Ticket.created_at < expiration_time
                )
            )
            .options(
                selectinload(Ticket.event)
            )
        )
        return result.scalars().all()

    async def create_ticket(self, user_id: int, event_id: int) -> Ticket:
        """Create a new ticket"""
        ticket = Ticket(
            user_id=user_id,
            event_id=event_id,
            status=TicketStatus.RESERVED,
            created_at=datetime.utcnow()
        )
        self.db.add(ticket)
        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket

    async def mark_as_paid(self, ticket_id: int, payment_reference: str) -> Optional[Ticket]:
        """Mark a ticket as paid"""
        ticket = await self.get_by_id(ticket_id)
        if ticket and ticket.status == TicketStatus.RESERVED:
            ticket.mark_as_paid(payment_reference)
            await self.db.commit()
            await self.db.refresh(ticket)
            return ticket
        return None

    async def expire_ticket(self, ticket_id: int) -> bool:
        """Mark a ticket as expired"""
        ticket = await self.get_by_id(ticket_id)
        if ticket and ticket.status == TicketStatus.RESERVED:
            ticket.mark_as_expired()
            await self.db.commit()
            return True
        return False

    async def expire_old_tickets(self) -> int:
        """Expire all reserved tickets older than 2 minutes"""
        expired_tickets = await self.get_expired_tickets()
        expired_count = 0
        
        for ticket in expired_tickets:
            if await self.expire_ticket(ticket.id):
                expired_count += 1
        
        return expired_count