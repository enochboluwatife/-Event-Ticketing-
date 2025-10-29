from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.api import events, tickets, for_you, auth
from app.models import User
from app.services.auth import AuthService

# Initialize FastAPI app
app = FastAPI(
    title="Event Ticketing API",
    description="REST API for event management and ticket booking with geospatial features",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(events.router, prefix="/api/v1/events", tags=["Events"])
app.include_router(tickets.router, prefix="/api/v1/tickets", tags=["Tickets"])
app.include_router(for_you.router, prefix="/api/v1/for-you", tags=["Personalized"])

# Health check endpoints
@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "Event Ticketing API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0"
    }