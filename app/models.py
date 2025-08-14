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
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'success', 'info', 'warning', 'error'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)
    recipient_role = db.Column(db.String(20), default='admin')  # 'admin' or 'user'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who triggered the event
    event_data = db.Column(db.JSON)  # Additional event data
    
    # Relationships
    user = db.relationship('User', backref='notifications', lazy='joined')
    
    def __repr__(self):
        return f'<Notification {self.id}: {self.type}>'
    
    @staticmethod
    def create_notification(message, type, recipient_role='admin', user_id=None, event_data=None):
        """Create a new notification"""
        notification = Notification(
            message=message,
            type=type,
            recipient_role=recipient_role,
            user_id=user_id,
            event_data=event_data or {}
        )
        db.session.add(notification)
        return notification
    
    @staticmethod
    def get_unread_count_for_role(role='admin'):
        """Get count of unread notifications for a specific role"""
        return Notification.query.filter_by(read=False, recipient_role=role).count()
    
    @staticmethod
    def get_recent_notifications_for_role(role='admin', limit=50):
        """Get recent notifications for a specific role ordered by creation time"""
        return Notification.query.filter_by(recipient_role=role).order_by(Notification.timestamp.desc()).limit(limit).all()
    
    @staticmethod
    def mark_as_read(notification_id):
        """Mark a notification as read"""
        notification = Notification.query.get(notification_id)
        if notification:
            notification.read = True
            db.session.commit()
            return True
        return False

class RecoveryCode(db.Model):
    """Model for storing user recovery codes"""
    __tablename__ = 'recovery_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    code_hash = db.Column(db.String(255), nullable=False)  # Hashed recovery code
    is_used = db.Column(db.Boolean, default=False)
    used_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='recovery_codes', lazy='joined')
    
    def __repr__(self):
        return f'<RecoveryCode {self.id} for User {self.user_id}>'
    
    @staticmethod
    def generate_codes(user_id, count=10):
        """Generate new recovery codes for a user"""
        import secrets
        import string
        
        # Generate alphanumeric codes (8 characters each)
        codes = []
        for _ in range(count):
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            # Format as XXXX-XXXX
            formatted_code = f"{code[:4]}-{code[4:]}"
            codes.append(formatted_code)
        
        # Hash and store codes
        for code in codes:
            code_hash = generate_password_hash(code)
            recovery_code = RecoveryCode(
                user_id=user_id,
                code_hash=code_hash
            )
            db.session.add(recovery_code)
        
        return codes
    
    @staticmethod
    def verify_code(user_id, code):
        """Verify a recovery code for a user"""
        recovery_codes = RecoveryCode.query.filter_by(
            user_id=user_id, 
            is_used=False
        ).all()
        
        for recovery_code in recovery_codes:
            if check_password_hash(recovery_code.code_hash, code):
                return recovery_code
        return None
    
    def mark_used(self):
        """Mark this recovery code as used"""
        self.is_used = True
        self.used_at = datetime.utcnow()

class RecoveryAttempt(db.Model):
    """Model for tracking recovery attempts and rate limiting"""
    __tablename__ = 'recovery_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    ip_address = db.Column(db.String(45), nullable=True)  # IPv4 or IPv6
    user_agent = db.Column(db.String(255), nullable=True)
    attempt_type = db.Column(db.String(20), nullable=False)  # 'code_verification', 'password_reset'
    success = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<RecoveryAttempt {self.attempt_type} for {self.email}>'
    
    @staticmethod
    def is_rate_limited(email, max_attempts=5, window_hours=1):
        """Check if email is rate limited for recovery attempts"""
        from datetime import timedelta
        
        window_start = datetime.utcnow() - timedelta(hours=window_hours)
        recent_attempts = RecoveryAttempt.query.filter(
            RecoveryAttempt.email == email,
            RecoveryAttempt.created_at >= window_start
        ).count()
        
        return recent_attempts >= max_attempts
    
    @staticmethod
    def log_attempt(email, ip_address, user_agent, attempt_type, success):
        """Log a recovery attempt"""
        attempt = RecoveryAttempt(
            email=email,
            ip_address=ip_address,
            user_agent=user_agent,
            attempt_type=attempt_type,
            success=success
        )
        db.session.add(attempt)
        return attempt
