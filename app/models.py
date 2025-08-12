from datetime import datetime
from app import db
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import get_jwt_identity
import re

class User(db.Model):
    """User model for authentication and profile management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    avatar_filename = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    has_submitted_feedback = db.Column(db.Boolean, default=False)  # Track if user has submitted feedback
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    feedback = db.relationship('Feedback', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == 'admin'
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is valid"
    
    @staticmethod
    def validate_name(name):
        """Validate name format"""
        if len(name) < 2 or len(name) > 50:
            return False, "Name must be between 2 and 50 characters"
        
        if not re.match(r'^[a-zA-Z\s]+$', name):
            return False, "Name can only contain letters and spaces"
        
        return True, "Name is valid"

class Feedback(db.Model):
    """Feedback model for user submissions"""
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    sentiment_label = db.Column(db.String(20))  # 'positive', 'negative', 'neutral'
    sentiment_score = db.Column(db.Float)
    admin_corrected_label = db.Column(db.String(20))  # Admin override
    admin_corrected_score = db.Column(db.Float)
    is_corrected = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Feedback {self.id} by User {self.user_id}>'
    
    @staticmethod
    def validate_text(text):
        """Validate feedback text"""
        if len(text) < 10 or len(text) > 500:
            return False, "Feedback text must be between 10 and 500 characters"
        return True, "Text is valid"
    
    @staticmethod
    def validate_rating(rating):
        """Validate rating value"""
        try:
            rating_int = int(rating)
            if 1 <= rating_int <= 5:
                return True, "Rating is valid"
            else:
                return False, "Rating must be between 1 and 5"
        except (ValueError, TypeError):
            return False, "Rating must be a valid integer"
    
    def get_final_sentiment(self):
        """Get the final sentiment (admin corrected if available)"""
        if self.is_corrected and self.admin_corrected_label:
            return self.admin_corrected_label, self.admin_corrected_score
        return self.sentiment_label, self.sentiment_score

class TokenBlocklist(db.Model):
    """Model for tracking revoked JWT tokens"""
    __tablename__ = 'token_blocklist'
    
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    def __repr__(self):
        return f'<TokenBlocklist {self.jti}>'

class Notification(db.Model):
    """Model for tracking system notifications and key events"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)  # 'registration', 'login', 'feedback_submission'
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who triggered the event
    event_data = db.Column(db.JSON)  # Additional event data
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='notifications', lazy='joined')
    
    def __repr__(self):
        return f'<Notification {self.event_type} by User {self.user_id}>'
    
    @staticmethod
    def create_notification(event_type, title, message, user_id=None, event_data=None):
        """Create a new notification"""
        notification = Notification(
            event_type=event_type,
            title=title,
            message=message,
            user_id=user_id,
            event_data=event_data or {}
        )
        db.session.add(notification)
        return notification
    
    @staticmethod
    def get_unread_count():
        """Get count of unread notifications"""
        return Notification.query.filter_by(is_read=False).count()
    
    @staticmethod
    def get_recent_notifications(limit=50):
        """Get recent notifications ordered by creation time"""
        return Notification.query.order_by(Notification.created_at.desc()).limit(limit).all()
