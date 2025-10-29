from __future__ import absolute_import
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.config import get_settings
from app.services.ticket import TicketService
from .celery import app

settings = get_settings()

def get_async_session():
    engine = create_async_engine(settings.DATABASE_URL)
    return async_sessionmaker(engine, expire_on_commit=False)()

async def _expire_tickets_async():
    """Async function to expire unpaid tickets"""
    async with get_async_session() as db:
        ticket_service = TicketService(db)
        try:
            expired_count = await ticket_service.expire_old_tickets()
            return expired_count
        except Exception as e:
            print(f"Error in expire_tickets: {str(e)}")
            raise

@app.task(name='tasks.expire_tickets')
def expire_tickets():
    """Celery task to expire unpaid tickets"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_expire_tickets_async())
    finally:
        loop.close()

async def _expire_ticket_async(ticket_id: int):
    """Async function to expire a specific ticket"""
    async with get_async_session() as db:
        ticket_service = TicketService(db)
        try:
            ticket = await ticket_service.get_ticket_by_id(ticket_id)
            if ticket and ticket.status == 'reserved':
                ticket.status = 'expired'
                await db.commit()
                return True
            return False
        except Exception as e:
            print(f"Error in expire_ticket: {str(e)}")
            raise

@app.task(name='tasks.expire_ticket')
def expire_ticket(ticket_id: int):
    """Celery task to expire a specific ticket"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_expire_ticket_async(ticket_id))
    finally:
        loop.close()