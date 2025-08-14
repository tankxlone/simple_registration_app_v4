from flask import render_template, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from app.main import bp
from app.models import User, Feedback, Notification
from app import db

@bp.route('/')
def index():
    """Home page route"""
    try:
        # Try to get user from JWT token in cookies
        user = None
        access_token = request.cookies.get('access_token_cookie')
        
        if access_token:
            try:
                # Use Flask-JWT-Extended to verify token
                verify_jwt_in_request()
                user_id = get_jwt_identity()
                
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
                print(f"DEBUG: JWT verification error: {e}")
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
                # Use Flask-JWT-Extended to verify token
                verify_jwt_in_request()
                user_id = get_jwt_identity()
                
                if user_id:
                    user = User.query.get(user_id)
                    if not user:
                        return jsonify({'error': 'User not found'}), 404
                else:
                    return jsonify({'error': 'Invalid token'}), 401
            except Exception as e:
                print(f"DEBUG: JWT verification error in dashboard: {e}")
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
                # Use Flask-JWT-Extended to verify token
                verify_jwt_in_request()
                user_id = get_jwt_identity()
                
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
                print(f"DEBUG: JWT verification error: {e}")
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

@bp.route('/api/notifications/count')
def notification_count():
    """Get notification count for authenticated users"""
    try:
        # Try to get user from JWT token in cookies
        user = None
        access_token = request.cookies.get('access_token_cookie')
        
        if access_token:
            try:
                # Use Flask-JWT-Extended to verify token
                verify_jwt_in_request()
                user_id = get_jwt_identity()
                
                if user_id:
                    user = User.query.get(user_id)
                    if user:
                        # Only admin users can see notification count
                        if user.role == 'admin':
                            unread_count = Notification.query.filter_by(read=False).count()
                            return jsonify({
                                'unread_count': unread_count,
                                'authenticated': True,
                                'is_admin': True
                            })
                        else:
                            return jsonify({
                                'unread_count': 0,
                                'authenticated': True,
                                'is_admin': False
                            })
                    else:
                        return jsonify({'error': 'User not found'}), 404
                else:
                    return jsonify({'error': 'Invalid token'}), 401
            except Exception as e:
                print(f"DEBUG: JWT verification error in notification count: {e}")
                return jsonify({'error': 'Invalid token'}), 401
        else:
            return jsonify({'error': 'Authentication required'}), 401
        
    except Exception as e:
        print(f"DEBUG: Notification count error: {e}")
        return jsonify({'error': 'Failed to get notification count'}), 500
