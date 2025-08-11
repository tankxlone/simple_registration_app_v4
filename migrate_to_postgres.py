#!/usr/bin/env python3
"""
Migration script to move from SQLite to PostgreSQL
Run this script after setting up PostgreSQL
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Load environment variables
load_dotenv('postgres.env')

def test_postgres_connection():
    """Test PostgreSQL connection"""
    try:
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL not found in environment variables")
            return False
            
        print(f"🔗 Testing connection to: {database_url}")
        
        # Create engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL: {version}")
            
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")
        return False

def create_tables():
    """Create tables in PostgreSQL"""
    try:
        from app import create_app, db
        from app.models import User, Feedback
        
        # Create Flask app
        app = create_app()
        
        with app.app_context():
            print("🗄️ Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Test inserting a sample user
            test_user = User(
                name="Test User",
                email="test@example.com",
                password_hash="test_hash",
                role="user"
            )
            db.session.add(test_user)
            db.session.commit()
            print("✅ Test user inserted successfully!")
            
            # Clean up test data
            db.session.delete(test_user)
            db.session.commit()
            print("✅ Test data cleaned up!")
            
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False
    
    return True

def main():
    """Main migration function"""
    print("🚀 Starting PostgreSQL Migration...")
    print("=" * 50)
    
    # Test connection
    if not test_postgres_connection():
        print("\n❌ Cannot proceed without database connection")
        print("Please check your PostgreSQL setup and DATABASE_URL")
        return
    
    print("\n📋 Creating database tables...")
    if create_tables():
        print("\n🎉 Migration completed successfully!")
        print("\nNext steps:")
        print("1. Update your .env file with the DATABASE_URL")
        print("2. Restart your Flask application")
        print("3. Your app is now using PostgreSQL!")
    else:
        print("\n❌ Migration failed!")
        print("Please check the error messages above")

if __name__ == "__main__":
    main()
