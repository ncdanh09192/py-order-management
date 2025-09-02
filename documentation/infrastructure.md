# Infrastructure & Project Structure

## Overview
Order Management API is a RESTful API system built with Python FastAPI, using event-driven architecture with PostgreSQL database and Redis cache.

## Tech Stack

### Backend Framework
- **FastAPI** - Modern, fast web framework for Python
- **Uvicorn** - ASGI server to run FastAPI
- **Python 3.11** - Runtime environment

### Database & ORM
- **PostgreSQL 15** - Primary database
- **Prisma ORM** - Type-safe database client with auto-migration
- **asyncpg** - Async PostgreSQL driver

### Cache & Message Queue
- **Redis 7** - In-memory cache and message broker
- **aioredis** - Async Redis client

### Authentication & Security
- **JWT** - JSON Web Tokens for authentication
- **python-jose** - JWT encoding/decoding
- **python-multipart** - Form data handling

### Data Validation & Serialization
- **Pydantic** - Data validation and serialization
- **pydantic-settings** - Environment configuration

### Testing & Development
- **pytest** - Testing framework
- **httpx** - Async HTTP client for testing
- **black, isort, flake8** - Code formatting and linting

## Project Structure

```
py_order_management/
├── app/                          # Main application code
│   ├── api/                     # API endpoints
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── orders.py           # Order management endpoints
│   │   └── health.py           # Health check endpoints
│   ├── core/                   # Core application logic
│   │   ├── config.py           # Configuration settings
│   │   ├── database.py         # Database connection management
│   │   ├── security.py         # JWT token operations
│   │   └── auth.py             # Authentication dependencies
│   ├── dto/                    # Data Transfer Objects
│   │   ├── requests/           # Request DTOs
│   │   │   ├── auth_request.py
│   │   │   └── order_request.py
│   │   └── responses/          # Response DTOs
│   │       ├── auth_response.py
│   │       └── order_response.py
│   ├── events/                 # Event-driven architecture
│   │   ├── base.py             # Base Event and EventHandler classes
│   │   ├── event_bus.py        # Central event bus
│   │   ├── order_events.py     # Order-specific events
│   │   └── handlers/           # Event handlers
│   │       ├── cache_handler.py # Redis cache operations
│   │       └── history_handler.py # Order history tracking
│   ├── services/               # Business logic layer
│   │   ├── auth_service.py     # Authentication business logic
│   │   └── order_service.py    # Order management business logic
│   ├── cache/                  # Cache layer
│   │   └── redis_client.py     # Redis client wrapper
│   ├── models/                 # Data models (placeholders)
│   ├── tests/                  # Unit tests
│   │   ├── conftest.py         # Test configuration
│   │   ├── test_health.py      # Health endpoint tests
│   │   ├── test_api_endpoints.py # API endpoint tests
│   │   ├── test_auth_service.py # Authentication service tests
│   │   ├── test_event_bus.py   # Event bus tests
│   │   ├── test_order_service.py # Order service tests
│   │   └── test_security.py    # Security tests
│   └── main.py                 # FastAPI application entry point
├── devops/                      # DevOps configuration
│   └── local/                  # Local development setup
│       ├── docker-compose.yml  # Multi-container setup
│       ├── Dockerfile          # Application container
│       ├── start.sh            # Local environment startup script
│       ├── .env                # Environment variables (actual)
│       ├── .env.example        # Environment variables template
│       └── init.sql/           # Database initialization (directory)
├── prisma/                     # Database schema and migrations
│   ├── schema.prisma          # Prisma schema definition
│   └── migrations/            # Database migration files
├── documentation/               # Project documentation
├── requirements.txt             # Python dependencies
├── pyproject.toml              # Project configuration
├── .gitignore                  # Git ignore rules
└── README.md                   # Project overview
```

## Database Schema

### Core Tables
- **order_headers** - Order metadata (customer, date, status, total)
- **order_lines** - Individual order items (product, quantity, price)
- **order_history** - Audit trail for order changes

### Enums
- **OrderStatus**: PENDING, SHIPPED, CANCELLED
- **OrderAction**: CREATED, UPDATED, DELETED

## Container Architecture

### Docker Services
1. **app** - FastAPI application (port 8000)
2. **postgres** - PostgreSQL database (port 5432)
3. **redis** - Redis cache (port 6379)

### Network Configuration
- Internal Docker network for inter-service communication
- Port mapping for external access
- Health checks for all services

## Event System Architecture

### Event Bus
- In-memory event bus for local development
- Async event handling with concurrent execution
- Event history tracking

### Event Types
- **OrderCreated** - When a new order is created
- **OrderUpdated** - When an order is updated
- **OrderDeleted** - When an order is deleted

### Event Handlers
- **CacheHandler** - Manages Redis cache
- **HistoryHandler** - Logs order history

## Security Architecture

### Authentication Flow
1. Client calls `/auth/login-test` with customer_id
2. Server returns JWT access token and refresh token
3. Client uses access token in Authorization header
4. Server validates token and extracts customer_id

### Authorization
- Order ownership validation
- Customer can only access their own orders
- JWT token validation for all protected endpoints

## Caching Strategy

### Cache Keys
- `order:{order_id}` - Order data with TTL 1 hour
- Cache-first strategy for GET operations
- Automatic cache invalidation when order changes

### Cache Operations
- **Set**: When order is created/updated
- **Get**: Before querying database
- **Delete**: When order is deleted

## Development Workflow

### Local Development
1. `cd devops/local && ./start.sh` - Start all services
2. Auto-reload with FastAPI development server
3. Prisma auto-migration and client generation
4. Health checks for database and Redis

### Testing
- Unit tests with pytest
- API testing with httpx
- Test database isolation
- Mock external dependencies

## Production Considerations

### Scalability
- Event bus can migrate to message queue (SQS, RabbitMQ)
- Database connection pooling
- Redis cluster for high availability
- Load balancing for multiple app instances

### Monitoring
- Health check endpoints
- Structured logging with structlog
- Event tracking and metrics
- Database performance monitoring

### Security
- Environment-based configuration
- JWT secret rotation
- Database connection encryption
- Rate limiting and input validation
