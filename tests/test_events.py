import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Event, User
from datetime import datetime, timedelta, timezone

@pytest.mark.asyncio
async def test_create_event(client: AsyncClient, sample_user):
    """Test creating a new event."""
    # First, login to get the token
    user = await sample_user
    login_data = {
        "username": user.email,
        "password": "testpassword"
    }
    login_response = await client.post("/api/v1/auth/login", data=login_data)
    assert login_response.status_code == status.HTTP_200_OK
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Prepare event data
    event_data = {
        "title": "New Event",
        "description": "A new test event",
        "start_time": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "end_time": (datetime.now(timezone.utc) + timedelta(days=1, hours=2)).isoformat(),
        "total_tickets": 100,
        "venue": {
            "address": "123 Main St",
            "latitude": 0.0,
            "longitude": 0.0
        }
    }
    
    # Create event
    response = await client.post(
        "/api/v1/events/", 
        json=event_data,
        headers=headers
    )
    
    # Assert the response
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == event_data["title"]
    assert data["description"] == event_data["description"]
    assert data["available_tickets"] == event_data["total_tickets"]
    assert "id" in data
    assert "venue" in data
    assert data["venue"]["address"] == event_data["venue"]["address"]