from flask import render_template, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, decode_token
from app.main import bp
from app.models import User, Feedback
from app import db
import jwt

@bp.route('/')
def index():
    """Home page route"""
    try:
        # Try to get user from JWT token in cookies
        user = None
        access_token = request.cookies.get('access_token_cookie')
        
        if access_token:
            try:
                # Decode the JWT token manually
                from config import Config
                decoded = jwt.decode(access_token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
                user_id = decoded.get('sub')
                
                if user_id:
                    user = User.query.get(user_id)
                    if user:
                        print(f"DEBUG: User authenticated: {user.name}")
                        print(f"DEBUG: User has_submitted_feedback: {user.has_submitted_feedback}")
                        print(f"DEBUG: User role: {user.role}")
                    else:
                        print("DEBUG: User not found in database")
                else:
                    print("DEBUG: No user_id in token")
            except Exception as e:
                print(f"DEBUG: JWT decode error: {e}")
                # Invalid token, user is not authenticated
                pass
        else:
            print("DEBUG: No access token cookie found")
        
        return render_template('main/index.html', user=user)
    except Exception as e:
        print(f"DEBUG: General error: {e}")
        # If there's any error, render without user
        return render_template('main/index.html', user=None)

@bp.route('/dashboard')
def dashboard():
    """User dashboard route"""
    try:
        # Get user from JWT token in cookies
        user = None
        access_token = request.cookies.get('access_token_cookie')
        
        if access_token:
            try:
                # Decode the JWT token manually
                from config import Config
                decoded = jwt.decode(access_token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
                user_id = decoded.get('sub')
                
                if user_id:
                    user = User.query.get(user_id)
                    if not user:
                        return jsonify({'error': 'User not found'}), 404
                else:
                    return jsonify({'error': 'Invalid token'}), 401
            except Exception as e:
                print(f"DEBUG: JWT decode error in dashboard: {e}")
                return jsonify({'error': 'Invalid token'}), 401
        else:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get time-based greeting
        from datetime import datetime
        current_hour = datetime.now().hour
        
        if 5 <= current_hour < 12:
            greeting = "Good Morning"
        elif 12 <= current_hour < 17:
            greeting = "Good Afternoon"
        elif 17 <= current_hour < 21:
            greeting = "Good Evening"
        else:
            greeting = "Good Night"
        
        return render_template('main/dashboard.html', 
                             user=user, 
                             greeting=greeting)
        
    except Exception as e:
        print(f"DEBUG: Dashboard error: {e}")
        return jsonify({'error': 'Failed to load dashboard'}), 500

@bp.route('/user-home')
def user_home():
    """User home route"""
    return jsonify({
        'message': 'User home route working',
        'status': 'success'
    })

@bp.route('/about')
def about():
    """About page route"""
    try:
        # Try to get user from JWT token in cookies
        user = None
        access_token = request.cookies.get('access_token_cookie')
        
        if access_token:
            try:
                # Decode the JWT token manually
                from config import Config
                decoded = jwt.decode(access_token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
                user_id = decoded.get('sub')
                
                if user_id:
                    user = User.query.get(user_id)
                    if user:
                        print(f"DEBUG: User authenticated: {user.name}")
                        print(f"DEBUG: User has_submitted_feedback: {user.has_submitted_feedback}")
                        print(f"DEBUG: User role: {user.role}")
                    else:
                        print("DEBUG: User not found in database")
                else:
                    print("DEBUG: No user_id in token")
            except Exception as e:
                print(f"DEBUG: JWT decode error: {e}")
                # Invalid token, user is not authenticated
                pass
        else:
            print("DEBUG: No access token cookie found")
        
        return render_template('main/about.html', user=user)
    except Exception as e:
        print(f"DEBUG: General error in about: {e}")
        # If there's any error, render without user
        return render_template('main/about.html', user=None)

@bp.route('/debug')
def debug():
    """Debug route for testing cookies and authentication"""
    return render_template('debug_cookies.html')
