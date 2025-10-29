import pytest
from fastapi import status
from httpx import AsyncClient
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Ticket, TicketStatus, User, Event

@pytest.mark.asyncio
async def test_reserve_ticket(client: AsyncClient, sample_user, sample_event):
    # Get the actual user and event objects by awaiting the fixtures
    user = await sample_user
    event = await sample_event
    
    # First, login to get the token
    login_data = {
        "username": user.email,
        "password": "testpassword"
    }
    login_response = await client.post("/api/v1/auth/login", data=login_data)
    assert login_response.status_code == status.HTTP_200_OK
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Prepare ticket data
    ticket_data = {
        "event_id": event.id,
        "user_id": user.id
    }
    response = await client.post("/api/v1/tickets/", json=ticket_data, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["status"] == "reserved"
    assert data["event_id"] == event.id
    assert data["user_id"] == user.id

@pytest.mark.asyncio
async def test_pay_ticket(client: AsyncClient, sample_user, sample_event, db_session: AsyncSession):
    # First, login to get the token
    user = await sample_user
    event = await sample_event
    login_data = {
        "username": user.email,
        "password": "testpassword"
    }
    login_response = await client.post("/api/v1/auth/login", data=login_data)
    assert login_response.status_code == status.HTTP_200_OK
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a reserved ticket
    ticket = Ticket(
        user_id=user.id,
        event_id=event.id,
        status=TicketStatus.RESERVED,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(ticket)
    await db_session.commit()
    await db_session.refresh(ticket)

    # Pay for the ticket
    payment_data = {
        "payment_reference": "test_payment_123"
    }
    response = await client.post(
        f"/api/v1/tickets/{ticket.id}/pay", 
        json=payment_data,
        headers=headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "paid"
    assert data["payment_reference"] == payment_data["payment_reference"]
    assert "paid_at" in data