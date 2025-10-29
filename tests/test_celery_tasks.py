import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Ticket, TicketStatus, User, Event
from app.celery_app.tasks import expire_tickets, expire_ticket
from app.services.ticket import TicketService

@pytest.mark.asyncio
async def test_expire_ticket(db_session: AsyncSession, sample_user, sample_event):
    # Get the actual user and event objects by awaiting the fixtures
    user = await sample_user
    event = await sample_event
    
    # Create a ticket that should expire
    ticket = Ticket(
        user_id=user.id,
        event_id=event.id,
        status=TicketStatus.RESERVED,
        created_at=datetime.now(timezone.utc) - timedelta(minutes=3)  # 3 minutes old
    )
    db_session.add(ticket)
    await db_session.commit()
    
    # Patch the TicketService to avoid actual Celery task execution
    with patch('app.celery_app.tasks.TicketService') as mock_service:
        mock_instance = mock_service.return_value
        mock_instance.get_by_id.return_value = ticket
        
        # Execute the task directly (in test mode)
        from app.celery_app.celery import app
        app.conf.task_always_eager = True  # Run tasks synchronously for testing
        
        # Call the task
        result = await expire_ticket(ticket.id)
        
        # Verify the task was called
        mock_instance.get_by_id.assert_called_once_with(ticket.id)
        assert result is True
        
        # Verify the ticket is expired
        await db_session.refresh(ticket)
        assert ticket.status == TicketStatus.EXPIRED

@pytest.mark.asyncio
async def test_expire_old_tickets(db_session: AsyncSession, sample_user, sample_event):
    # Get the actual user and event objects by awaiting the fixtures
    user = await sample_user
    event = await sample_event
    
    # Create multiple tickets that should expire
    tickets = []
    for i in range(3):
        ticket = Ticket(
            user_id=user.id,
            event_id=event.id,
            status=TicketStatus.RESERVED,
            created_at=datetime.now(timezone.utc) - timedelta(minutes=3)  # 3 minutes old
        )
        db_session.add(ticket)
        tickets.append(ticket)
    await db_session.commit()
    
    # Patch the TicketService to avoid actual Celery task execution
    with patch('app.celery_app.tasks.TicketService') as mock_service:
        mock_instance = mock_service.return_value
        mock_instance.expire_old_tickets.return_value = 3
        
        # Execute the task directly (in test mode)
        from app.celery_app.celery import app
        app.conf.task_always_eager = True  # Run tasks synchronously for testing
        
        # Call the task
        result = await expire_tickets()
        
        # Verify the task was called
        mock_instance.expire_old_tickets.assert_called_once()
        assert result == 3
    
    # Verify all tickets are expired
    result = await db_session.execute(select(Ticket).where(Ticket.status == TicketStatus.EXPIRED))
    assert len(result.scalars().all()) == 3