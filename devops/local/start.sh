#!/bin/bash

echo "🚀 Starting Order Management System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

print_status "Docker environment check passed"

# Stop any existing containers
print_status "Stopping existing containers..."
docker-compose down --remove-orphans

# Build and start containers
print_status "Building and starting containers..."
docker-compose up --build -d

# Wait for services to be ready
print_status "Waiting for services to be ready..."

# Wait for PostgreSQL
print_status "Waiting for PostgreSQL..."
while ! docker-compose exec -T postgres pg_isready -U user -d orderdb > /dev/null 2>&1; do
    sleep 2
done
print_success "PostgreSQL is ready"

# Wait for Redis
print_status "Waiting for Redis..."
while ! docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; do
    sleep 2
done
print_success "Redis is ready"

# Wait for app to be ready
print_status "Waiting for application to be ready..."
while ! curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; do
    sleep 3
done
print_success "Application is ready"

# Check application health
print_status "Checking application health..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/api/v1/health)

if echo "$HEALTH_RESPONSE" | grep -q '"status":"healthy"'; then
    print_success "All services are healthy!"
else
    print_warning "Some services may not be fully healthy. Check the health endpoint for details."
fi

echo ""
echo "🎉 Order Management System is running!"
echo ""
echo "📊 Service Status:"
echo "   • FastAPI App: http://localhost:8000"
echo "   • API Documentation: http://localhost:8000/docs"
echo "   • Health Check: http://localhost:8000/api/v1/health"
echo "   • PostgreSQL: localhost:5432"
echo "   • Redis: localhost:6379"
echo ""
echo "🔑 Test Credentials:"
echo "   • Use any positive customer_id for login-test endpoint"
echo "   • Example: POST /api/v1/auth/login-test with {\"customer_id\": 123}"
echo ""
echo "📝 Next Steps:"
echo "   1. Open http://localhost:8000/docs in your browser"
echo "   2. Test the login-test endpoint to get JWT tokens"
echo "   3. Use the tokens to test other endpoints"
echo ""
echo "🛑 To stop the system, run: docker-compose down"
echo "🔄 To restart, run: ./start.sh"
echo "📋 To view logs, run: docker-compose logs -f app"
