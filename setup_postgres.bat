@echo off
echo 🐘 Setting up PostgreSQL for Feedback App...
echo ==============================================

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

REM Check if Docker Compose is available
docker compose version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not available. Please install it first.
    pause
    exit /b 1
)

echo ✅ Docker and Docker Compose are available

REM Stop any existing containers
echo 🛑 Stopping any existing containers...
docker compose -f docker-compose.postgres.yml down

REM Start PostgreSQL
echo 🚀 Starting PostgreSQL...
docker compose -f docker-compose.postgres.yml up -d postgres

REM Wait for PostgreSQL to be ready
echo ⏳ Waiting for PostgreSQL to be ready...
timeout /t 10 /nobreak >nul

REM Check if PostgreSQL is healthy
docker compose -f docker-compose.postgres.yml exec postgres pg_isready -U postgres
if %errorlevel% neq 0 (
    echo ❌ PostgreSQL is not ready. Please check the logs:
    docker compose -f docker-compose.postgres.yml logs postgres
    pause
    exit /b 1
)

echo ✅ PostgreSQL is ready!

REM Start pgAdmin
echo 🚀 Starting pgAdmin...
docker compose -f docker-compose.postgres.yml up -d pgadmin

echo.
echo 🎉 PostgreSQL setup completed!
echo.
echo 📊 Database Information:
echo    Host: localhost
echo    Port: 5432
echo    Database: feedback_app
echo    Username: postgres
echo    Password: password
echo.
echo 🌐 pgAdmin (Database Management):
echo    URL: http://localhost:8080
echo    Email: admin@feedbackapp.com
echo    Password: admin
echo.
echo 🔧 Next steps:
echo 1. Copy the DATABASE_URL from postgres.env to your .env file
echo 2. Run: python migrate_to_postgres.py
echo 3. Restart your Flask application
echo.
echo 📝 To stop PostgreSQL: docker-compose -f docker-compose.postgres.yml down
echo 📝 To view logs: docker-compose -f docker-compose.postgres.yml logs -f
echo.
pause
