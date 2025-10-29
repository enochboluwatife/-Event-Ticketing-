#!/usr/bin/env python3
"""
Script to create database tables directly
"""
import asyncio
from sqlalchemy import create_engine
from app.database import Base
from app.models import User, Event, Ticket
from app.config import get_settings

settings = get_settings()

# Use sync engine for creating tables
engine = create_engine(settings.SYNC_DATABASE_URL)

def create_tables():
    """Create all tables defined in the models"""
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    create_tables()

