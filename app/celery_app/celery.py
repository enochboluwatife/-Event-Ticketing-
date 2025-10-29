from __future__ import absolute_import
import os
from celery import Celery
from app.config import get_settings

settings = get_settings()

# Create the Celery app
app = Celery('event_ticketing')

# Configure Celery
app.conf.update(
    broker_url=settings.CELERY_BROKER_URL,
    result_backend=settings.CELERY_RESULT_BACKEND,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    imports=('app.celery_app.tasks',),
    beat_schedule={
        'expire-tickets-every-minute': {
            'task': 'tasks.expire_tickets',
            'schedule': 60.0,  # Run every 60 seconds
        },
    },
)

# Import tasks to ensure they are registered
from . import tasks  # noqa

# This is the Celery app instance
celery_app = app