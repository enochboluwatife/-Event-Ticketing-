from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.ticket import TicketCreate, TicketResponse, TicketPayment
from app.services.ticket import TicketService
from app.celery_app.tasks import expire_ticket

router = APIRouter()

@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_data: TicketCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new ticket for an event"""
    ticket_service = TicketService(db)
    try:
        ticket = await ticket_service.create_ticket(ticket_data)
        return ticket
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get ticket by ID"""
    ticket_service = TicketService(db)
    try:
        ticket = await ticket_service.get_ticket_by_id(ticket_id)
        return ticket
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/user/{user_id}", response_model=List[TicketResponse])
async def get_user_tickets(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all tickets for a user"""
    ticket_service = TicketService(db)
    try:
        tickets = await ticket_service.get_tickets_by_user(user_id)
        return tickets
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/{ticket_id}/pay", response_model=TicketResponse)
async def pay_ticket(
    ticket_id: int,
    payment_data: TicketPayment,
    db: AsyncSession = Depends(get_db)
):
    """Mark a ticket as paid"""
    ticket_service = TicketService(db)
    try:
        ticket = await ticket_service.pay_ticket(
            ticket_id=ticket_id,
            payment_reference=payment_data.payment_reference,
            paid_at=datetime.now(timezone.utc)
        )
        return ticket
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )