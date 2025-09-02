# API Documentation

## Overview
Order Management API provides RESTful endpoints for managing customer orders with JWT authentication and comprehensive validation.

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
All protected endpoints require JWT token in Authorization header:
```
Authorization: Bearer <access_token>
```

## API Endpoints

### 1. Authentication Endpoints

#### POST /auth/login-test
**Description**: Test login endpoint to get JWT tokens (development only)

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login-test" \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 123}'
```

**Request Body**:
```json
{
  "customer_id": 123
}
```

**Response** (200 OK):
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "tokenType": "bearer",
  "expiresIn": 1800,
  "customerId": 123
}
```

#### POST /auth/refresh
**Description**: Refresh access token using refresh token

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}'
```

**Request Body**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 2. Order Management Endpoints

#### POST /orders/
**Description**: Create new order with multiple order lines

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/orders/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "customer_id": 123,
    "order_date": "2025-01-01T10:00:00",
    "status": "PENDING",
    "lines": [
      {
        "product_id": 1001,
        "quantity": 2,
        "unit_price": "25.50"
      },
      {
        "product_id": 1002,
        "quantity": 1,
        "unit_price": "15.00"
      }
    ]
  }'
```

**Request Body**:
```json
{
  "customer_id": 123,
  "order_date": "2025-01-01T10:00:00",
  "status": "PENDING",
  "lines": [
    {
      "product_id": 1001,
      "quantity": 2,
      "unit_price": "25.50"
    },
    {
      "product_id": 1002,
      "quantity": 1,
      "unit_price": "15.00"
    }
  ]
}
```

**Response** (201 Created):
```json
{
  "id": 6,
  "customerId": 123,
  "orderDate": "2025-01-01T10:00:00Z",
  "status": "PENDING",
  "totalAmount": "66.00",
  "createdAt": "2025-09-01T07:10:19.917000Z",
  "updatedAt": "2025-09-01T07:10:19.917000Z",
  "lines": [
    {
      "id": 11,
      "productId": 1001,
      "quantity": 2,
      "unitPrice": "25.50",
      "createdAt": "2025-09-01T07:10:19.938000Z"
    },
    {
      "id": 12,
      "productId": 1002,
      "quantity": 1,
      "unitPrice": "15.00",
      "createdAt": "2025-09-01T07:10:19.964000Z"
    }
  ]
}
```

#### GET /orders/{order_id}
**Description**: Get order information by ID (with cache-first strategy)

**Request**:
```bash
curl -H "Authorization: Bearer <access_token>" \
  "http://localhost:8000/api/v1/orders/6"
```

**Response** (200 OK):
```json
{
  "id": 6,
  "customerId": 123,
  "orderDate": "2025-01-01T10:00:00Z",
  "status": "PENDING",
  "totalAmount": "66.00",
  "createdAt": "2025-09-01T07:10:19.917000Z",
  "updatedAt": "2025-09-01T07:10:19.917000Z",
  "lines": [
    {
      "id": 11,
      "productId": 1001,
      "quantity": 2,
      "unitPrice": "25.50",
      "createdAt": "2025-09-01T07:10:19.938000Z"
    },
    {
      "id": 12,
      "productId": 1002,
      "quantity": 1,
      "unitPrice": "15.00",
      "createdAt": "2025-09-01T07:10:19.964000Z"
    }
  ]
}
```

#### PUT /orders/{order_id}
**Description**: Update order status

**Request**:
```bash
curl -X PUT "http://localhost:8000/api/v1/orders/6" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"status": "SHIPPED"}'
```

**Request Body**:
```json
{
  "status": "SHIPPED"
}
```

**Response** (200 OK):
```json
{
  "id": 6,
  "customerId": 123,
  "orderDate": "2025-01-01T10:00:00Z",
  "status": "SHIPPED",
  "totalAmount": "66.00",
  "createdAt": "2025-09-01T07:10:19.917000Z",
  "updatedAt": "2025-09-01T07:10:29.123000Z",
  "lines": [
    {
      "id": 11,
      "productId": 1001,
      "quantity": 2,
      "unitPrice": "25.50",
      "createdAt": "2025-09-01T07:10:19.938000Z"
    },
    {
      "id": 12,
      "productId": 1002,
      "quantity": 1,
      "unitPrice": "15.00",
      "createdAt": "2025-09-01T07:10:19.964000Z"
    }
  ]
}
```

#### DELETE /orders/{order_id}
**Description**: Delete order and all order lines

**Request**:
```bash
curl -X DELETE "http://localhost:8000/api/v1/orders/6" \
  -H "Authorization: Bearer <access_token>"
```

**Response** (200 OK):
```json
{
  "message": "Order deleted successfully"
}
```

#### GET /orders/
**Description**: List orders with pagination

**Request**:
```bash
curl -H "Authorization: Bearer <access_token>" \
  "http://localhost:8000/api/v1/orders/?page=1&size=10"
```

**Query Parameters**:
- `page` (optional): Page number, default: 1
- `size` (optional): Page size, default: 10, max: 100

**Response** (200 OK):
```json
{
  "orders": [
    {
      "id": 6,
      "customerId": 123,
      "orderDate": "2025-01-01T10:00:00Z",
      "status": "PENDING",
      "totalAmount": "66.00",
      "createdAt": "2025-09-01T07:10:19.917000Z",
      "updatedAt": "2025-09-01T07:10:19.917000Z",
      "lines": [
        {
          "id": 11,
          "productId": 1001,
          "quantity": 2,
          "unitPrice": "25.50",
          "createdAt": "2025-09-01T07:10:19.938000Z"
        },
        {
          "id": 12,
          "productId": 1002,
          "quantity": 1,
          "unitPrice": "15.00",
          "createdAt": "2025-09-01T07:10:19.964000Z"
        }
      ]
    }
  ],
  "total": 1,
  "page": 1,
  "size": 10,
  "hasNext": false,
  "hasPrev": false
}
```

### 3. Health Check Endpoints

#### GET /health/
**Description**: Health check endpoint

**Request**:
```bash
curl "http://localhost:8000/api/v1/health/"
```

**Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2025-09-01T07:10:19.917000Z",
  "version": "1.0.0"
}
```

#### GET /health/ready
**Description**: Readiness check endpoint

**Request**:
```bash
curl "http://localhost:8000/api/v1/health/ready"
```

**Response** (200 OK):
```json
{
  "status": "ready",
  "database": "connected",
  "redis": "connected",
  "timestamp": "2025-09-01T07:10:19.917000Z"
}
```

#### GET /
**Description**: Root endpoint

**Request**:
```bash
curl "http://localhost:8000/"
```

**Response** (200 OK):
```json
{
  "message": "Order Management API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

#### GET /docs
**Description**: Swagger API documentation

**Request**:
```bash
curl "http://localhost:8000/docs"
```

**Response**: HTML page with interactive API documentation

## Data Models

### Request DTOs

#### CreateOrderRequest
```json
{
  "customer_id": "integer > 0",
  "order_date": "datetime string (ISO format)",
  "status": "PENDING | SHIPPED | CANCELLED",
  "lines": [
    {
      "product_id": "integer > 0",
      "quantity": "integer 1-1000",
      "unit_price": "decimal 0-999999.99"
    }
  ]
}
```

#### UpdateOrderRequest
```json
{
  "status": "PENDING | SHIPPED | CANCELLED"
}
```

#### LoginTestRequest
```json
{
  "customer_id": "integer > 0"
}
```

#### RefreshTokenRequest
```json
{
  "refresh_token": "string"
}
```

### Response DTOs

#### OrderResponse
```json
{
  "id": "integer",
  "customerId": "integer",
  "orderDate": "datetime",
  "status": "PENDING | SHIPPED | CANCELLED",
  "totalAmount": "decimal",
  "createdAt": "datetime",
  "updatedAt": "datetime",
  "lines": [
    {
      "id": "integer",
      "productId": "integer",
      "quantity": "integer",
      "unitPrice": "decimal",
      "createdAt": "datetime"
    }
  ]
}
```

#### OrderListResponse
```json
{
  "orders": ["OrderResponse[]"],
  "total": "integer",
  "page": "integer",
  "size": "integer",
  "hasNext": "boolean",
  "hasPrev": "boolean"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Not authorized to access this order"
}
```

### 404 Not Found
```json
{
  "detail": "Order not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Validation Rules

### Order Validation
- **customer_id**: Must be positive integer
- **order_date**: Cannot be in the future
- **status**: Must be one of: PENDING, SHIPPED, CANCELLED
- **lines**: Array with 1-50 items

### Order Line Validation
- **product_id**: Must be positive integer
- **quantity**: Must be between 1 and 1000
- **unit_price**: Must be between 0 and 999,999.99

### Authentication Validation
- **JWT token**: Must be valid and not expired
- **Customer ownership**: User can only access their own orders

## Rate Limiting
Currently no rate limiting implemented. Consider adding for production use.

## Caching
- **Order data**: Cached in Redis with TTL 1 hour
- **Cache invalidation**: Automatic when order is updated/deleted
- **Cache strategy**: Cache-first with database fallback

## Event System
All order operations automatically trigger events:
- **OrderCreated**: When a new order is created
- **OrderUpdated**: When an order is updated
- **OrderDeleted**: When an order is deleted

Events are handled by:
- **CacheHandler**: Manages Redis cache
- **HistoryHandler**: Logs order history
