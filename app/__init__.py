from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
# from flask_wtf.csrf import CSRFProtect  # Temporarily commented out due to Flask 3.0 compatibility
from config import Config
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)
# csrf = CSRFProtect()  # Temporarily commented out

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)
    
    # Set JWT secret key explicitly
    app.config['JWT_SECRET_KEY'] = app.config['JWT_SECRET_KEY']
    # csrf.init_app(app)  # Temporarily commented out
    
    # Import and register blueprints
    from app.auth import bp as auth_bp
    from app.main import bp as main_bp
    from app.profile import bp as profile_bp
    from app.feedback import bp as feedback_bp
    from app.admin import bp as admin_bp
    from app.api import bp as api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(feedback_bp, url_prefix='/feedback')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {'message': 'Token has expired'}, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {'message': 'Invalid token'}, 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {'message': 'Missing token'}, 401
    
    # Register CLI commands
    @app.cli.command("init-db")
    def init_db_command():
        """Initialize the database."""
        db.create_all()
        print("Database initialized!")
    
    @app.cli.command("create-admin")
    def create_admin_command():
        """Create an admin user."""
        from app.models import User
        
        admin = User(
            email='admin@example.com',
            name='Admin User',
            role='admin'
        )
        admin.set_password('AdminPass123!')
        
        db.session.add(admin)
        db.session.commit()
        
        print("Admin user created!")
        print(f"Email: {admin.email}")
        print(f"Password: AdminPass123!")
    
    return app
