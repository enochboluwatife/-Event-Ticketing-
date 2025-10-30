# Event Ticketing API

A REST API for event management and ticket booking with geospatial features. Built with FastAPI, PostgreSQL/PostGIS, and Celery.

## Features

- 🎫 **Event Management** - Create and manage events with geolocation
- 💳 **Ticket Booking** - Purchase and pay for event tickets
- ⏰ **Auto-Expiration** - Unpaid tickets automatically expire after 2 minutes
- 🗺️ **Geospatial Queries** - Find events near a location using PostGIS
- 🔐 **JWT Authentication** - Secure user authentication
- 🐳 **Dockerized** - Complete Docker setup for easy deployment

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Setup & Run

```bash
# 1. Clone the repository
git clone https://github.com/enochboluwatife/-Event-Ticketing-.git
cd event-ticketing-api

# 2. Copy environment file
cp .env.example .env

# 3. Start all services
docker-compose up -d

# 4. Run database migrations (wait 10 seconds for DB to be ready)
docker-compose exec api alembic upgrade head

# 5. Access the API
# Swagger UI: http://localhost:8000/docs
# API: http://localhost:8000
```

That's it! 🚀

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs (Interactive API testing)
- **ReDoc**: http://localhost:8000/redoc (Alternative documentation)

## Testing the API

### Using Swagger UI (Recommended)

1. Open http://localhost:8000/docs
2. Register a user: `POST /api/v1/auth/register`
3. Login: `POST /api/v1/auth/login`
4. Copy the `access_token` from response
5. Click **"Authorize"** button and enter: `Bearer YOUR_TOKEN`
6. Test all endpoints!

### Using cURL

```bash
# Register a user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "testpass123",
    "location": {"latitude": 6.5244, "longitude": 3.3792}
  }'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john@example.com&password=testpass123"

# Create an event (replace YOUR_TOKEN)
curl -X POST "http://localhost:8000/api/v1/events/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Tech Conference 2025",
    "description": "Annual tech conference",
    "start_time": "2025-12-01T09:00:00",
    "end_time": "2025-12-01T18:00:00",
    "total_tickets": 100,
    "venue": {
      "address": "123 Tech Street, Lagos",
      "latitude": 6.5244,
      "longitude": 3.3792
    }
  }'

# Find nearby events
curl -X GET "http://localhost:8000/api/v1/for-you/events/nearby?latitude=6.5244&longitude=3.3792&radius_km=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Project Structure

```
.
├── app/
│   ├── api/              # API endpoints (auth, events, tickets, for_you)
│   ├── models/           # SQLAlchemy models (User, Event, Ticket)
│   ├── schemas/          # Pydantic schemas for validation
│   ├── services/         # Business logic layer
│   ├── repositories/     # Database access layer
│   └── celery_app/       # Background tasks for ticket expiration
├── tests/                # Unit and integration tests
├── migrations/           # Alembic database migrations
├── docker-compose.yml    # Docker services configuration
├── Dockerfile            # API container configuration
└── requirements.txt      # Python dependencies
```

## Key Assumptions

1. **Ticket Expiration**: Unpaid tickets expire after 2 minutes (configurable via `TICKET_EXPIRATION_MINUTES`)
2. **Location Data**: User and event locations use latitude/longitude coordinates
3. **Authentication**: JWT tokens with 30-minute expiration (configurable)
4. **Geospatial Queries**: Distance calculations use PostGIS ST_DWithin (accurate for small distances)
5. **Payment**: Simplified payment flow using payment reference (no actual payment gateway integration)

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Async PostgreSQL connection URL | `postgresql+asyncpg://postgres:postgres@db:5432/eventdb` |
| `SYNC_DATABASE_URL` | Sync PostgreSQL URL (for Celery) | `postgresql://postgres:postgres@db:5432/eventdb` |
| `CELERY_BROKER_URL` | Redis URL for Celery broker | `redis://redis:6379/0` |
| `CELERY_RESULT_BACKEND` | Redis URL for Celery results | `redis://redis:6379/0` |
| `SECRET_KEY` | JWT secret key | `your-secret-key-change-in-production` |
| `TICKET_EXPIRATION_MINUTES` | Minutes before ticket expires | `2` |

## Running Tests

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest -v

# Run with coverage
pytest --cov=app tests/
```

## Tech Stack

- **Framework**: FastAPI 0.120.2
- **Database**: PostgreSQL 15 with PostGIS 3.4
- **ORM**: SQLAlchemy 2.0 (async)
- **Task Queue**: Celery 5.5 + Redis 7.0
- **Authentication**: JWT (python-jose)
- **Validation**: Pydantic 2.12
- **Testing**: Pytest
- **Containerization**: Docker & Docker Compose

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token

### Events
- `POST /api/v1/events/` - Create event
- `GET /api/v1/events/` - List all events
- `GET /api/v1/events/{id}` - Get event by ID

### Tickets
- `POST /api/v1/tickets/` - Purchase ticket
- `GET /api/v1/tickets/{id}` - Get ticket details
- `GET /api/v1/tickets/user/{user_id}` - Get user's tickets
- `POST /api/v1/tickets/{id}/pay` - Mark ticket as paid

### Personalized (Geospatial)
- `GET /api/v1/for-you/events/nearby` - Find events near location
- `GET /api/v1/for-you/events/recommended` - Get recommended events for user

## Stopping the Application

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clears database)
docker-compose down -v
```

## License

This project is licensed under the MIT License.
