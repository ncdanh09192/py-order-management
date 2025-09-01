# Order Management API

A modern, event-driven RESTful API for managing customer orders built with FastAPI, PostgreSQL, Redis, and Prisma ORM.

## 🚀 Features

- **Event-Driven Architecture**: Order events trigger caching and history tracking
- **JWT Authentication**: Secure API with access and refresh tokens
- **Redis Caching**: Fast order retrieval with automatic cache management
- **Complete Order History**: Track all order changes for audit and analytics
- **Comprehensive Validation**: Input validation with Pydantic schemas
- **Auto-Generated Documentation**: Swagger/OpenAPI docs at `/docs`
- **Health Monitoring**: Database and Redis connection health checks
- **Docker Ready**: Complete containerization with PostgreSQL and Redis

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   Event Bus     │    │   Event        │
│                 │───▶│                 │───▶│   Handlers     │
│   - API Routes │    │   - Publish     │    │   - Cache      │
│   - Services   │    │   - Subscribe   │    │   - History    │
│   - DTOs       │    │                 │    │   - Logging    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │     Redis       │    │   Logging      │
│   - Orders     │    │   - Cache       │    │   - Events     │
│   - History    │    │   - Sessions    │    │   - Requests   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15
- **ORM**: Prisma
- **Cache**: Redis 7
- **Authentication**: JWT
- **Validation**: Pydantic
- **Containerization**: Docker & Docker Compose
- **Documentation**: Swagger/OpenAPI

## 📋 Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- Git

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd py_order_management
```

### 2. Start the System

```bash
cd devops/local
chmod +x start.sh
./start.sh
```

This script will:
- Build and start all containers
- Wait for services to be ready
- Run database migrations
- Generate Prisma client
- Start the FastAPI application

### 3. Access the API

- **API Base URL**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

## 🔑 Authentication

### Test Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login-test" \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 123}'
```

Response:
```json
{
  "accessToken": "eyJ...",
  "refreshToken": "eyJ...",
  "tokenType": "bearer",
  "expiresIn": 1800,
  "customerId": 123
}
```

### Using Tokens

```bash
curl -X GET "http://localhost:8000/api/v1/orders/1" \
  -H "Authorization: Bearer eyJ..."
```

## 📚 API Endpoints

### Authentication
- `POST /api/v1/auth/login-test` - Get JWT tokens (test endpoint)
- `POST /api/v1/auth/refresh` - Refresh access token

### Orders
- `POST /api/v1/orders` - Create new order
- `GET /api/v1/orders/{id}` - Get order by ID
- `PUT /api/v1/orders/{id}` - Update order status
- `DELETE /api/v1/orders/{id}` - Delete order
- `GET /api/v1/orders` - List orders with pagination

### Health
- `GET /api/v1/health` - System health check
- `GET /api/v1/health/ready` - Readiness check

## 📝 API Examples

### Create Order

```bash
curl -X POST "http://localhost:8000/api/v1/orders" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 123,
    "order_date": "2025-01-20",
    "status": "PENDING",
    "lines": [
      {
        "product_id": 1001,
        "quantity": 2,
        "unit_price": 25.50
      },
      {
        "product_id": 1002,
        "quantity": 1,
        "unit_price": 15.00
      }
    ]
  }'
```

### Get Order

```bash
curl -X GET "http://localhost:8000/api/v1/orders/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Update Order

```bash
curl -X PUT "http://localhost:8000/api/v1/orders/1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "SHIPPED"}'
```

## 🗄️ Database Schema

### Order Header
```sql
CREATE TABLE order_headers (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    order_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Order Line
```sql
CREATE TABLE order_lines (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES order_headers(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Order History
```sql
CREATE TABLE order_history (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES order_headers(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,
    changes JSON,
    performed_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔄 Event System

The system uses an event-driven architecture where order operations trigger events:

- **OrderCreated**: Triggers caching and history logging
- **OrderUpdated**: Updates cache and logs changes
- **OrderDeleted**: Removes from cache and logs deletion

### Event Handlers

- **CacheHandler**: Manages Redis cache operations
- **HistoryHandler**: Tracks order history changes

## 🧪 Testing

### Unit Tests

The project includes comprehensive unit tests covering all major components:

#### Test Structure
```
app/tests/
├── conftest.py              # Test configuration and fixtures
├── test_api_endpoints.py    # API endpoint tests
├── test_auth_service.py     # Authentication service tests
├── test_event_bus.py        # Event bus functionality tests
├── test_health.py           # Health check tests
├── test_order_service.py    # Order service business logic tests
└── test_security.py         # Security and JWT tests
```

#### Running Tests

```bash
# Run all tests
pytest app/tests/

# Run with verbose output
pytest -v app/tests/

# Run with coverage report
pytest --cov=app app/tests/

# Run specific test file
pytest app/tests/test_api_endpoints.py

# Run specific test function
pytest app/tests/test_api_endpoints.py::test_create_order

# Run tests with parallel execution
pytest -n auto app/tests/

# Generate HTML coverage report
pytest --cov=app --cov-report=html app/tests/
```

#### Test Coverage

The test suite covers:
- **API Endpoints**: All CRUD operations for orders
- **Authentication**: JWT token generation, validation, and refresh
- **Services**: Business logic in order and auth services
- **Event System**: Event publishing, handling, and bus functionality
- **Security**: Password hashing, token validation
- **Health Checks**: Database and Redis connectivity

#### Test Configuration

Tests use `pytest` with the following features:
- **Fixtures**: Reusable test data and setup
- **Mocking**: External dependencies isolation
- **Database**: Test database with automatic cleanup
- **Redis**: Test Redis instance for cache testing
- **Async Support**: Full async/await test coverage

#### Example Test

```python
def test_create_order_success(client, auth_headers):
    """Test successful order creation"""
    order_data = {
        "customer_id": 123,
        "order_date": "2025-01-20",
        "status": "PENDING",
        "lines": [
            {
                "product_id": 1001,
                "quantity": 2,
                "unit_price": 25.50
            }
        ]
    }
    
    response = client.post("/api/v1/orders", 
                          json=order_data, 
                          headers=auth_headers)
    
    assert response.status_code == 201
    assert response.json()["customer_id"] == 123
    assert response.json()["status"] == "PENDING"
```

### Integration Tests

```bash
# Run integration tests (requires running services)
pytest app/tests/ --integration

# Test with real database
pytest app/tests/ --db=real
```

### API Testing

Use the Swagger UI at `/docs` or import the Postman collection:

```bash
# Test health endpoint
curl http://localhost:8000/api/v1/health

# Test readiness
curl http://localhost:8000/api/v1/health/ready

# Test authentication
curl -X POST "http://localhost:8000/api/v1/auth/login-test" \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 123}'
```

### Performance Testing

```bash
# Run load tests
pytest app/tests/ --performance

# Run stress tests
pytest app/tests/ --stress
```

### Test Data Management

```bash
# Reset test database
pytest --reset-db

# Seed test data
pytest --seed-data

# Clean test cache
pytest --clear-cache
```

## 🐳 Docker Commands

### Management

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f app

# Rebuild and start
docker-compose up --build -d

# Stop and remove volumes
docker-compose down -v
```

### Individual Services

```bash
# PostgreSQL logs
docker-compose logs postgres

# Redis logs
docker-compose logs redis

# Execute commands in containers
docker-compose exec postgres psql -U user -d orderdb
docker-compose exec redis redis-cli
```

## 🔧 Development

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Install Prisma
pip install prisma

# Generate Prisma client
prisma generate

# Run migrations
prisma migrate dev

# Start application
uvicorn app.main:app --reload
```

### Environment Variables

Create a `.env` file based on `env.example`:

```bash
cp env.example .env
# Edit .env with your configuration
```

### Database Migrations

```bash
# Create new migration
prisma migrate dev --name add_new_field

# Apply migrations
prisma migrate deploy

# Reset database
prisma migrate reset
```

## 📊 Monitoring

### Health Checks

- **Database**: Connection and query execution
- **Redis**: Connection and ping response
- **Application**: Overall system status

### Logging

- **Request Logging**: All API requests with timing
- **Event Logging**: Event publishing and handling
- **Error Logging**: Detailed error information

## 🚀 Production Deployment

### Environment Variables

```bash
# Production settings
EVENT_SYSTEM=sqs
SQS_QUEUE_URL=https://sqs.region.amazonaws.com/account/queue
AWS_REGION=us-east-1
DEBUG=false
LOG_LEVEL=WARNING
```

### Scaling

- **Horizontal Scaling**: Multiple app instances
- **Database**: Connection pooling and read replicas
- **Cache**: Redis cluster for high availability
- **Message Queue**: SQS for async event processing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

- **Documentation**: Check `/docs` endpoint
- **Issues**: Create GitHub issue
- **Health**: Check `/health` endpoint

## 🎯 Roadmap

- [ ] Background job processing
- [ ] Email notifications
- [ ] Advanced analytics
- [ ] Multi-tenant support
- [ ] API rate limiting
- [ ] GraphQL support
