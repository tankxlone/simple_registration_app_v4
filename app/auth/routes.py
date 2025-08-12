from flask import render_template, redirect, url_for, flash, request, jsonify, make_response
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from app.auth import bp
from app.models import User, TokenBlocklist
from app import db, limiter
from app.forms import LoginForm, RegistrationForm
from datetime import datetime, timedelta
import re

@bp.route('/register', methods=['GET', 'POST'])
# @limiter.limit("5 per minute")  # Temporarily disabled for testing
def register():
    """User registration endpoint"""
    if request.method == 'POST':
        data = request.get_json()
        
        # Validate input data
        email = data.get('email', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        name = data.get('name', '').strip()
        
        # Validation
        errors = {}
        
        # Email validation
        if not email:
            errors['email'] = 'Email is required'
        elif not User.validate_email(email):
            errors['email'] = 'Invalid email format'
        elif User.query.filter_by(email=email).first():
            errors['email'] = 'Email already registered'
        
        # Password validation
        is_valid, password_msg = User.validate_password(password)
        if not is_valid:
            errors['password'] = password_msg
        
        # Confirm password
        if password != confirm_password:
            errors['confirm_password'] = 'Passwords do not match'
        
        # Name validation
        is_valid, name_msg = User.validate_name(name)
        if not is_valid:
            errors['name'] = name_msg
        
        if errors:
            return jsonify({'errors': errors}), 400
        
        # Create user
        try:
            user = User(email=email, name=name, has_submitted_feedback=False)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            # Create notification for new user registration
            from app.models import Notification
            Notification.create_notification(
                event_type='registration',
                title='New User Registration',
                message=f'New user {name} ({email}) has registered on the platform.',
                user_id=user.id,
                event_data={'email': email, 'name': name}
            )
            db.session.commit()
            
            # Create tokens
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))
            
            response = make_response(jsonify({
                'message': 'Registration successful! Welcome aboard!',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'role': user.role
                },
                'redirect': '/feedback/welcome'  # Redirect to welcome feedback form
            }))
            
            # Set secure cookies (secure=False for HTTP development, httponly=False for JS access)
            response.set_cookie(
                'access_token_cookie',
                access_token,
                httponly=False,  # Set to False so JavaScript can read cookies
                secure=False,  # Set to False for HTTP development
                samesite='Lax',
                max_age=3600,  # 1 hour
                domain=None,  # Use current domain
                path='/'
            )
            
            response.set_cookie(
                'refresh_token_cookie',
                refresh_token,
                httponly=False,  # Set to False so JavaScript can read cookies
                secure=False,  # Set to False for HTTP development
                samesite='Lax',
                max_age=30*24*3600,  # 30 days
                domain=None,  # Use current domain
                path='/'
            )
            
            return response, 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Registration failed. Please try again.'}), 500
    
    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
# @limiter.limit("5 per minute")  # Temporarily disabled for testing
def login():
    """User login endpoint"""
    if request.method == 'POST':
        data = request.get_json()
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validation
        errors = {}
        
        if not email:
            errors['email'] = 'Email is required'
        elif not User.validate_email(email):
            errors['email'] = 'Invalid email format'
        
        if not password:
            errors['password'] = 'Password is required'
        elif len(password) < 8:
            errors['password'] = 'Password must be at least 8 characters'
        
        if errors:
            return jsonify({'errors': errors}), 400
        
        # Authenticate user
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                return jsonify({'error': 'Account is deactivated'}), 403
            
            # Create notification for user login
            from app.models import Notification
            Notification.create_notification(
                event_type='login',
                title='User Login',
                message=f'User {user.name} ({user.email}) has logged in.',
                user_id=user.id,
                event_data={'email': user.email, 'name': user.name}
            )
            db.session.commit()
            
            # Create tokens
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            
            response = make_response(jsonify({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'role': user.role
                }
            }))
            
            # Set secure cookies (secure=False for HTTP development, httponly=False for JS access)
            response.set_cookie(
                'access_token_cookie',
                access_token,
                httponly=False,  # Set to False so JavaScript can read cookies
                secure=False,  # Set to False for HTTP development
                samesite='Lax',
                max_age=3600,  # 1 hour
                domain=None,  # Use current domain
                path='/'
            )
            
            response.set_cookie(
                'refresh_token_cookie',
                refresh_token,
                httponly=False,  # Set to False so JavaScript can read cookies
                secure=False,  # Set to False for HTTP development
                samesite='Lax',
                max_age=30*24*3600,  # 30 days
                domain=None,  # Use current domain
                path='/'
            )
            
            return response, 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
    
    return render_template('auth/login.html')

@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout endpoint"""
    try:
        # Get JWT token
        jti = get_jwt()['jti']
        exp = get_jwt()['exp']
        
        # Add to blocklist
        blocklisted_token = TokenBlocklist(
            jti=jti,
            created_at=datetime.utcnow(),
            expires_at=datetime.fromtimestamp(exp)
        )
        db.session.add(blocklisted_token)
        db.session.commit()
        
        response = make_response(jsonify({'message': 'Logout successful'}))
        
        # Clear cookies
        response.delete_cookie('access_token_cookie')
        response.delete_cookie('refresh_token_cookie')
        
        return response, 200
        
    except Exception as e:
        return jsonify({'error': 'Logout failed'}), 500

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token endpoint"""
    try:
        current_user_id = get_jwt_identity()
        
        # Create new access token
        new_access_token = create_access_token(identity=current_user_id)
        
        response = make_response(jsonify({'message': 'Token refreshed'}))
        
        # Set new access token cookie (secure=False for HTTP development, httponly=False for JS access)
        response.set_cookie(
            'access_token_cookie',
            new_access_token,
            httponly=False,  # Set to False so JavaScript can read cookies
            secure=False,  # Set to False for HTTP development
            samesite='Lax',
            max_age=3600,  # 1 hour
            domain=None,  # Use current domain
            path='/'
        )
        
        return response, 200
        
    except Exception as e:
        return jsonify({'error': 'Token refresh failed'}), 500

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'role': user.role,
                'avatar_filename': user.avatar_filename,
                'has_submitted_feedback': user.has_submitted_feedback
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get user info'}), 500
