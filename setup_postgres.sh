#!/bin/bash

echo "🐘 Setting up PostgreSQL for Feedback App..."
echo "=============================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! docker compose version > /dev/null 2>&1; then
    echo "❌ Docker Compose is not available. Please install it first."
    exit 1
fi

echo "✅ Docker and Docker Compose are available"

# Stop any existing containers
echo "🛑 Stopping any existing containers..."
docker compose -f docker-compose.postgres.yml down

# Start PostgreSQL
echo "🚀 Starting PostgreSQL..."
docker compose -f docker-compose.postgres.yml up -d postgres

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

# Check if PostgreSQL is healthy
if docker compose -f docker-compose.postgres.yml exec postgres pg_isready -U postgres; then
    echo "✅ PostgreSQL is ready!"
else
    echo "❌ PostgreSQL is not ready. Please check the logs:"
    docker compose -f docker-compose.postgres.yml logs postgres
    exit 1
fi

# Start pgAdmin
echo "🚀 Starting pgAdmin..."
docker compose -f docker-compose.postgres.yml up -d pgadmin

echo ""
echo "🎉 PostgreSQL setup completed!"
echo ""
echo "📊 Database Information:"
echo "   Host: localhost"
echo "   Port: 5432"
echo "   Database: feedback_app"
echo "   Username: postgres"
echo "   Password: password"
echo ""
echo "🌐 pgAdmin (Database Management):"
echo "   URL: http://localhost:8080"
echo "   Email: admin@feedbackapp.com"
echo "   Password: admin"
echo ""
echo "🔧 Next steps:"
echo "1. Copy the DATABASE_URL from postgres.env to your .env file"
echo "2. Run: python migrate_to_postgres.py"
echo "3. Restart your Flask application"
echo ""
echo "📝 To stop PostgreSQL: docker compose -f docker-compose.postgres.yml down"
echo "📝 To view logs: docker compose -f docker-compose.postgres.yml logs -f"
