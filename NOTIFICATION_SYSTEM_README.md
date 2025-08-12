# Notification System Documentation

## Overview

The notification system has been successfully implemented to track key events in the feedback application. Whenever a key event happens (registration, login, feedback submission), the backend automatically writes a record into a Notification table, and admins can view these in a notification center inside the dashboard.

## Features

### 🔔 Automatic Event Tracking
- **User Registration**: Creates a notification when a new user registers
- **User Login**: Creates a notification when a user logs in
- **Feedback Submission**: Creates a notification when feedback is submitted

### 📊 Admin Dashboard Integration
- **Notification Center Widget**: Shows recent notifications with unread count
- **Quick Actions**: Mark individual notifications as read or mark all as read
- **Real-time Updates**: Live notification count and status updates

### 🎛️ Dedicated Notifications Page
- **Full Notification Management**: View all notifications with pagination
- **Filtering Options**: Filter by unread status and event type
- **Statistics Dashboard**: Overview of notification counts and distribution
- **Bulk Actions**: Mark all notifications as read

## Database Schema

### Notification Table
```sql
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,  -- 'registration', 'login', 'feedback_submission'
    title VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    user_id INTEGER REFERENCES users(id),  -- User who triggered the event
    event_data JSON,  -- Additional event data
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Event Types and Data

#### Registration Events
- **Event Type**: `registration`
- **Data**: `{"email": "user@example.com", "name": "John Doe"}`

#### Login Events
- **Event Type**: `login`
- **Data**: `{"email": "user@example.com", "name": "John Doe"}`

#### Feedback Submission Events
- **Event Type**: `feedback_submission`
- **Data**: `{"rating": 5, "sentiment": "positive", "sentiment_score": 0.8}`

## API Endpoints

### Admin Notification Routes

#### Get Notifications
```
GET /admin/api/notifications
Query Parameters:
- page: Page number (default: 1)
- per_page: Items per page (default: 20)
- unread_only: Show only unread (true/false)
- event_type: Filter by event type
```

#### Mark Notification as Read
```
POST /admin/api/notifications/{id}/mark-read
```

#### Mark All Notifications as Read
```
POST /admin/api/notifications/mark-all-read
```

#### Get Notification Statistics
```
GET /admin/api/notifications/stats
Returns:
- total_notifications
- unread_count
- recent_count (last 24 hours)
- event_distribution
```

## User Interface

### Admin Dashboard Widget
The notification center widget is integrated into the main admin dashboard (`/admin/dashboard`) and includes:
- Recent notifications display
- Unread count badge
- Quick action buttons (Refresh, Mark All Read)
- Individual notification actions

### Dedicated Notifications Page
Full notification management at `/admin/notifications` featuring:
- Statistics cards showing counts and trends
- Advanced filtering and search options
- Paginated notification list
- Bulk management actions

### Navigation Integration
Notifications are accessible through:
- Admin dropdown menu in the main navigation
- Quick action cards on the admin dashboard
- Direct URL access to `/admin/notifications`

## Implementation Details

### Model Methods
```python
class Notification(db.Model):
    @staticmethod
    def create_notification(event_type, title, message, user_id=None, event_data=None):
        """Create a new notification"""
    
    @staticmethod
    def get_unread_count():
        """Get count of unread notifications"""
    
    @staticmethod
    def get_recent_notifications(limit=50):
        """Get recent notifications ordered by creation time"""
```

### Event Creation Examples
```python
# Registration notification
Notification.create_notification(
    event_type='registration',
    title='New User Registration',
    message=f'New user {name} ({email}) has registered on the platform.',
    user_id=user.id,
    event_data={'email': email, 'name': name}
)

# Login notification
Notification.create_notification(
    event_type='login',
    title='User Login',
    message=f'User {user.name} ({user.email}) has logged in.',
    user_id=user.id,
    event_data={'email': user.email, 'name': user.name}
)

# Feedback notification
Notification.create_notification(
    event_type='feedback_submission',
    title='New Feedback Submission',
    message=f'User {user.name} has submitted new feedback with {rating}/5 rating.',
    user_id=user.id,
    event_data={'rating': rating, 'sentiment': sentiment_label, 'sentiment_score': sentiment_score}
)
```

## Setup and Installation

### 1. Database Migration
Run the migration script to create the notifications table:
```bash
python migrate_notifications.py
```

### 2. Verify Installation
Test that the notification system is working:
```bash
python test_notifications.py
```

### 3. Access the System
- Start the Flask application: `python run.py`
- Open http://localhost:5000 in your browser
- Register a new user or login to see notifications being created
- Access admin dashboard to view the notification center

## Usage Examples

### For End Users
1. **Register**: New users automatically create registration notifications
2. **Login**: Each login creates a login notification
3. **Submit Feedback**: Feedback submissions create detailed notifications

### For Administrators
1. **Dashboard Overview**: View recent notifications in the admin dashboard
2. **Detailed Management**: Use the dedicated notifications page for full control
3. **Monitoring**: Track user activity and system usage patterns
4. **Audit Trail**: Maintain records of all key system events

## Customization

### Adding New Event Types
To add new event types, simply create notifications with new `event_type` values:

```python
Notification.create_notification(
    event_type='user_profile_update',
    title='Profile Updated',
    message=f'User {user.name} updated their profile.',
    user_id=user.id,
    event_data={'updated_fields': ['avatar', 'name']}
)
```

### Customizing Notification Display
The notification display can be customized by:
- Adding new icons in the `getNotificationIcon()` function
- Adding new colors in the `getNotificationColor()` function
- Modifying the notification card templates

### Extending Event Data
The `event_data` JSON field can store any additional information:
- User preferences
- System metrics
- Error details
- Performance data

## Security Considerations

- **Admin Only Access**: All notification endpoints require admin authentication
- **User Privacy**: Notifications only show user information to admins
- **Rate Limiting**: Event creation is subject to existing rate limiting
- **Audit Trail**: All notifications are logged for security purposes

## Troubleshooting

### Common Issues

1. **Notifications Not Appearing**
   - Check if the notifications table exists
   - Verify the migration script ran successfully
   - Check browser console for JavaScript errors

2. **Permission Denied Errors**
   - Ensure user has admin role
   - Check JWT token validity
   - Verify admin_required decorator is working

3. **Database Connection Issues**
   - Verify database configuration
   - Check if Flask app can connect to database
   - Ensure proper database permissions

### Debug Mode
Enable debug mode in Flask to see detailed error messages:
```python
app.run(debug=True)
```

## Future Enhancements

### Potential Improvements
- **Email Notifications**: Send email alerts for critical events
- **Push Notifications**: Real-time browser notifications
- **Notification Preferences**: Allow admins to configure notification types
- **Advanced Filtering**: Date ranges, user groups, custom criteria
- **Export Functionality**: Export notifications to CSV/PDF
- **Notification Templates**: Customizable notification messages
- **Webhook Integration**: Send notifications to external services

### Scalability Considerations
- **Database Indexing**: Add indexes for frequently queried fields
- **Caching**: Implement Redis caching for notification counts
- **Background Processing**: Use Celery for notification creation
- **Partitioning**: Partition notifications table by date for large datasets

## Support

For questions or issues with the notification system:
1. Check the application logs for error messages
2. Verify database connectivity and permissions
3. Test with the provided test scripts
4. Review the implementation examples above

---

**Note**: This notification system is designed to be lightweight and efficient while providing comprehensive event tracking for administrative purposes.
