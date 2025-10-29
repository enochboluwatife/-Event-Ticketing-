from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db as get_db_session

# Re-export get_db from database module
get_db = get_db_session