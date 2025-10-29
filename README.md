# Event Ticketing API

A RESTful API for event management and ticket booking with geospatial features, built with FastAPI, SQLAlchemy, and Celery.

## Features

- Create and manage events with geolocation
- Purchase and manage tickets
- Automatic ticket expiration for unpaid reservations
- Geospatial queries for finding nearby events
- Asynchronous request handling
- Containerized with Docker

## Prerequisites

- Docker and Docker Compose
- Python 3.11+
- PostgreSQL with PostGIS extension
- Redis

## Getting Started

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd event-ticketing-api
   ```

2. **Environment Setup**
   Copy the example environment file and update it with your configuration:
   ```bash
   cp .env.example .env
   ```

3. **Build and Start Services**
   ```bash
   docker-compose up --build
   ```
   This will start:
   - API server on http://localhost:8000
   - PostgreSQL database
   - Redis server
   - Celery worker
   - Celery beat (for scheduled tasks)

4. **Run Migrations**
   ```bash
   docker-compose exec api alembic upgrade head
   ```

## API Documentation

Once the application is running, you can access:

- **Interactive API Docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8000/redoc

## Running Tests

To run the test suite:

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run tests
pytest -v
```

## Project Structure

```
.
├── app/
│   ├── api/                 # API routes
│   ├── core/                # Core functionality
│   ├── db/                  # Database configuration
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic models
│   ├── services/            # Business logic
│   └── tasks/               # Celery tasks
├── tests/                   # Test files
├── alembic/                 # Database migrations
├── .env.example             # Example environment variables
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile               # Docker configuration
└── requirements.txt         # Python dependencies
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql+asyncpg://postgres:postgres@db:5432/eventdb` |
| `SYNC_DATABASE_URL` | Synchronous PostgreSQL URL | `postgresql://postgres:postgres@db:5432/eventdb` |
| `CELERY_BROKER_URL` | Celery broker URL | `redis://redis:6379/0` |
| `CELERY_RESULT_BACKEND` | Celery result backend | `redis://redis:6379/0` |