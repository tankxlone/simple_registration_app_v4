#!/usr/bin/env python3
"""
Flask CLI management script for database operations and other commands
"""
import os
from flask.cli import FlaskGroup
from app import create_app, db
from app.models import User, Feedback, TokenBlocklist

# Create Flask app instance
app = create_app()
cli = FlaskGroup(app)

@cli.command("init-db")
def init_db():
    """Initialize the database with tables"""
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

@cli.command("create-admin")
def create_admin():
    """Create an admin user"""
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(role='admin').first()
        if admin:
            print(f"Admin user already exists: {admin.email}")
            return
        
        # Create admin user
        admin = User(
            email='admin@example.com',
            name='Admin User',
            role='admin'
        )
        admin.set_password('AdminPass123!')
        
        db.session.add(admin)
        db.session.commit()
        
        print("Admin user created successfully!")
        print(f"Email: {admin.email}")
        print(f"Password: AdminPass123!")
        print("Please change the password after first login!")

@cli.command("create-tables")
def create_tables():
    """Create database tables (alternative to init-db)"""
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

@cli.command("drop-tables")
def drop_tables():
    """Drop all database tables"""
    with app.app_context():
        db.drop_all()
        print("All database tables dropped!")

@cli.command("seed-db")
def seed_db():
    """Seed database with sample data"""
    with app.app_context():
        # Create sample users
        user1 = User(
            email='user1@example.com',
            name='John Doe',
            role='user'
        )
        user1.set_password('UserPass123!')
        
        user2 = User(
            email='user2@example.com',
            name='Jane Smith',
            role='user'
        )
        user2.set_password('UserPass123!')
        
        db.session.add(user1)
        db.session.add(user2)
        
        # Create sample feedback
        feedback1 = Feedback(
            user_id=1,
            text="This is a great product! I love how easy it is to use.",
            rating=5,
            sentiment_label='positive',
            sentiment_score=0.8
        )
        
        feedback2 = Feedback(
            user_id=2,
            text="The product works well but could use some improvements.",
            rating=4,
            sentiment_label='positive',
            sentiment_score=0.6
        )
        
        db.session.add(feedback1)
        db.session.add(feedback2)
        
        db.session.commit()
        print("Sample data seeded successfully!")

if __name__ == '__main__':
    cli()
