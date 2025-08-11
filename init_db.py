#!/usr/bin/env python3
"""
Simple database initialization script
Run this to set up your database and create an admin user
"""
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Feedback, TokenBlocklist

def init_database():
    """Initialize the database"""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Create admin user if it doesn't exist
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            print("Creating admin user...")
            admin = User(
                email='admin@example.com',
                name='Admin User',
                role='admin'
            )
            admin.set_password('AdminPass123!')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created successfully!")
            print(f"   Email: {admin.email}")
            print(f"   Password: AdminPass123!")
            print("   ⚠️  Please change the password after first login!")
        else:
            print(f"✅ Admin user already exists: {admin.email}")
        
        # Create sample data if no feedback exists
        if Feedback.query.count() == 0:
            print("Creating sample data...")
            
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
            db.session.commit()
            
            # Create sample feedback
            feedback1 = Feedback(
                user_id=user1.id,
                text="This is a great product! I love how easy it is to use.",
                rating=5,
                sentiment_label='positive',
                sentiment_score=0.8
            )
            
            feedback2 = Feedback(
                user_id=user2.id,
                text="The product works well but could use some improvements.",
                rating=4,
                sentiment_label='positive',
                sentiment_score=0.6
            )
            
            db.session.add(feedback1)
            db.session.add(feedback2)
            db.session.commit()
            
            print("✅ Sample data created successfully!")
        else:
            print(f"✅ Sample data already exists ({Feedback.query.count()} feedback entries)")
        
        print("\n🎉 Database initialization completed!")
        print("\nYou can now:")
        print("1. Run the Flask app: python -m flask run")
        print("2. Login as admin: admin@example.com / AdminPass123!")
        print("3. Login as user: user1@example.com / UserPass123!")

if __name__ == '__main__':
    init_database()
