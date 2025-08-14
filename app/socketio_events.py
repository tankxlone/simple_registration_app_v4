from flask import request
from flask_socketio import emit, join_room, leave_room
from app import socketio
from app.models import User
from flask_jwt_extended import decode_token
import jwt

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")
    
    # Try to get user from JWT token in cookies
    access_token = request.cookies.get('access_token_cookie')
    
    if access_token:
        try:
            # Decode JWT token to get user info
            # Note: In production, you should use proper JWT verification
            payload = decode_token(access_token)
            user_id = payload.get('sub')
            
            if user_id:
                user = User.query.get(user_id)
                if user:
                    # Join room based on user role
                    room_name = f'role_{user.role}'
                    join_room(room_name)
                    print(f"User {user.name} joined room: {room_name}")
                    
                    # Also join user-specific room for private messages
                    join_room(f'user_{user_id}')
                    
                    # Store user info in session
                    request.user_id = user_id
                    request.user_role = user.role
                    
                    emit('connection_status', {
                        'status': 'connected',
                        'user_id': user_id,
                        'role': user.role
                    })
                    return
        except Exception as e:
            print(f"Error processing JWT token: {e}")
    
    # If no valid token, join as anonymous user
    join_room('anonymous')
    emit('connection_status', {'status': 'connected', 'role': 'anonymous'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")
    
    # Leave all rooms
    if hasattr(request, 'user_id'):
        leave_room(f'user_{request.user_id}')
    if hasattr(request, 'user_role'):
        leave_room(f'role_{request.user_role}')
    
    leave_room('anonymous')

@socketio.on('join_admin_room')
def handle_join_admin_room():
    """Handle admin user joining admin room"""
    access_token = request.cookies.get('access_token_cookie')
    
    if access_token:
        try:
            payload = decode_token(access_token)
            user_id = payload.get('sub')
            
            if user_id:
                user = User.query.get(user_id)
                if user and user.is_admin():
                    join_room('role_admin')
                    emit('room_joined', {'room': 'role_admin', 'status': 'success'})
                    return
        except Exception as e:
            print(f"Error joining admin room: {e}")
    
    emit('room_joined', {'room': 'role_admin', 'status': 'denied'})

@socketio.on('leave_admin_room')
def handle_leave_admin_room():
    """Handle admin user leaving admin room"""
    leave_room('role_admin')
    emit('room_left', {'room': 'role_admin'})

@socketio.on('get_notification_count')
def handle_get_notification_count():
    """Handle request for notification count"""
    access_token = request.cookies.get('access_token_cookie')
    
    if access_token:
        try:
            payload = decode_token(access_token)
            user_id = payload.get('sub')
            
            if user_id:
                user = User.query.get(user_id)
                if user:
                    from app.services.notification_service import get_notification_count_for_role
                    count = get_notification_count_for_role(user.role)
                    
                    emit('notification_count', {
                        'count': count,
                        'role': user.role
                    })
                    return
        except Exception as e:
            print(f"Error getting notification count: {e}")
    
    emit('notification_count', {'count': 0, 'role': 'anonymous'})
