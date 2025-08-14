from app import db, socketio
from app.models import Notification, User
from datetime import datetime

def send_notification(message, type, recipient_role='admin', user_id=None, event_data=None):
    """
    Send a notification to users with a specific role
    
    Args:
        message (str): The notification message
        type (str): Notification type ('success', 'info', 'warning', 'error')
        recipient_role (str): Role to receive the notification (default: 'admin')
        user_id (int): ID of the user who triggered the event (optional)
        event_data (dict): Additional event data (optional)
    """
    try:
        # Create notification in database
        notification = Notification.create_notification(
            message=message,
            type=type,
            recipient_role=recipient_role,
            user_id=user_id,
            event_data=event_data
        )
        
        # Commit to database
        db.session.commit()
        
        # Emit WebSocket event to all users with the specified role
        socketio.emit('new_notification', {
            'id': notification.id,
            'message': notification.message,
            'type': notification.type,
            'timestamp': notification.timestamp.isoformat(),
            'user_id': notification.user_id,
            'event_data': notification.event_data
        }, room=f'role_{recipient_role}')
        
        return notification
        
    except Exception as e:
        db.session.rollback()
        print(f"Error sending notification: {e}")
        return None

def send_admin_notification(message, type='info', user_id=None, event_data=None):
    """
    Convenience function to send notifications to admin users
    """
    return send_notification(message, type, 'admin', user_id, event_data)

def send_user_notification(message, type='info', user_id=None, event_data=None):
    """
    Convenience function to send notifications to regular users
    """
    return send_notification(message, type, 'user', user_id, event_data)

def get_notification_count_for_role(role='admin'):
    """
    Get unread notification count for a specific role
    """
    return Notification.get_unread_count_for_role(role)

def get_notifications_for_role(role='admin', limit=50):
    """
    Get recent notifications for a specific role
    """
    return Notification.get_recent_notifications_for_role(role, limit)

def mark_notification_read(notification_id):
    """
    Mark a notification as read
    """
    return Notification.mark_as_read(notification_id)
