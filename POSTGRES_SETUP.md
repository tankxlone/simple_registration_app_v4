# 🐘 PostgreSQL Setup Guide for Feedback App

This guide will help you migrate your Flask application from SQLite to PostgreSQL.

## 🚀 Quick Start

### Option 1: Using Docker (Recommended)

1. **Start PostgreSQL:**
   ```bash
   # Linux/Mac
   ./setup_postgres.sh
   
   # Windows
   setup_postgres.bat
   ```

2. **Migrate your database:**
   ```bash
   python migrate_to_postgres.py
   ```

3. **Update your environment:**
   ```bash
   # Copy DATABASE_URL from postgres.env to your .env file
   cp postgres.env .env
   ```

4. **Restart your Flask app:**
   ```bash
   flask run
   ```

### Option 2: Manual PostgreSQL Installation

1. **Install PostgreSQL:**
   - **Ubuntu/Debian:** `sudo apt-get install postgresql postgresql-contrib`
   - **macOS:** `brew install postgresql`
   - **Windows:** Download from [postgresql.org](https://www.postgresql.org/download/windows/)

2. **Create database:**
   ```bash
   sudo -u postgres psql
   CREATE DATABASE feedback_app;
   CREATE USER feedback_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE feedback_app TO feedback_user;
   \q
   ```

3. **Update postgres.env:**
   ```bash
   DATABASE_URL=postgresql://feedback_user:your_password@localhost:5432/feedback_app
   ```

## 📊 Database Information

- **Host:** localhost
- **Port:** 5432
- **Database:** feedback_app
- **Username:** postgres
- **Password:** password
- **pgAdmin:** http://localhost:8080 (admin@feedbackapp.com / admin)

## 🔧 Configuration Files

### postgres.env
Contains your PostgreSQL connection string and other environment variables.

### docker-compose.postgres.yml
Docker Compose configuration for PostgreSQL and pgAdmin.

### init.sql
Database initialization script with extensions and functions.

## 🗄️ Database Migration

The migration script (`migrate_to_postgres.py`) will:

1. Test PostgreSQL connection
2. Create all necessary tables
3. Test basic operations
4. Clean up test data

## 🐳 Docker Commands

```bash
# Start PostgreSQL
docker compose -f docker-compose.postgres.yml up -d

# Stop PostgreSQL
docker compose -f docker-compose.postgres.yml down

# View logs
docker compose -f docker-compose.postgres.yml logs -f

# Access PostgreSQL shell
docker compose -f docker-compose.postgres.yml exec postgres psql -U postgres -d feedback_app

# Backup database
docker compose -f docker-compose.postgres.yml exec postgres pg_dump -U postgres feedback_app > backup.sql

# Restore database
docker compose -f docker-compose.postgres.yml exec -T postgres psql -U postgres -d feedback_app < backup.sql
```

## 🔍 Troubleshooting

### Connection Issues

1. **Check if PostgreSQL is running:**
   ```bash
   docker compose -f docker-compose.postgres.yml ps
   ```

2. **Check logs:**
   ```bash
   docker compose -f docker-compose.postgres.yml logs postgres
   ```

3. **Test connection:**
   ```bash
   python migrate_to_postgres.py
   ```

### Port Conflicts

If port 5432 is already in use:

1. **Find what's using the port:**
   ```bash
   # Linux/Mac
   lsof -i :5432
   
   # Windows
   netstat -ano | findstr :5432
   ```

2. **Change port in docker-compose.postgres.yml:**
   ```yaml
   ports:
     - "5433:5432"  # Use port 5433 instead
   ```

3. **Update DATABASE_URL:**
   ```
   DATABASE_URL=postgresql://postgres:password@localhost:5433/feedback_app
   ```

## 📈 Benefits of PostgreSQL

- **Better Performance:** Optimized for complex queries
- **ACID Compliance:** Full transaction support
- **Advanced Features:** JSON support, full-text search, etc.
- **Scalability:** Better for production workloads
- **Community:** Large, active community and ecosystem

## 🔐 Security Notes

- **Development:** Default passwords are used for convenience
- **Production:** Always use strong, unique passwords
- **Network:** PostgreSQL is only accessible from localhost by default
- **Backup:** Regular backups are recommended for production

## 🚀 Production Deployment

For production, consider:

1. **Environment Variables:** Use proper secrets management
2. **Connection Pooling:** Configure connection pooling for better performance
3. **Backup Strategy:** Automated daily backups
4. **Monitoring:** Set up database monitoring and alerting
5. **SSL:** Enable SSL connections for security

## 📚 Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy with PostgreSQL](https://docs.sqlalchemy.org/en/14/dialects/postgresql.html)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
- [Docker PostgreSQL](https://hub.docker.com/_/postgres)

## 🆘 Need Help?

If you encounter issues:

1. Check the troubleshooting section above
2. Review the logs: `docker-compose -f docker-compose.postgres.yml logs -f`
3. Test the connection: `python migrate_to_postgres.py`
4. Verify your environment variables are set correctly

---

**Happy coding with PostgreSQL! 🐘✨**
