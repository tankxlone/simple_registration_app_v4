# Real-Time Admin Notification System

This document describes the real-time in-app admin notification system integrated into the Flask application using Flask-SocketIO.

## 🚀 Features

- **Real-time notifications** via WebSocket (Socket.IO)
- **Role-based delivery** (admin users only)
- **Automatic triggers** for key events
- **Persistent storage** in database
- **Interactive UI** with dropdown and badges
- **Instant updates** without page refresh

## 🏗️ Architecture

### Tech Stack
- **Backend**: Flask-SocketIO for WebSocket events
- **Database**: SQLAlchemy ORM with PostgreSQL
- **Frontend**: Bootstrap 5 + Socket.IO client
- **Authentication**: JWT-based with role checking

### Components
1. **Notification Model** - Database storage
2. **Notification Service** - Business logic and WebSocket emission
3. **Socket.IO Events** - Real-time communication
4. **API Endpoints** - RESTful notification management
5. **Frontend Components** - Dropdown UI and real-time updates

## 📊 Database Schema

```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    message TEXT NOT NULL,
    type VARCHAR(20) NOT NULL, -- 'success', 'info', 'warning', 'error'
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read BOOLEAN DEFAULT FALSE,
    recipient_role VARCHAR(20) DEFAULT 'admin',
    user_id INTEGER REFERENCES users(id),
    event_data JSON
);
```

## 🔧 Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Database Migration
The notification table will be created automatically when you run:
```bash
flask init-db
```

### 3. Run the Application
```bash
python run.py
```

**Note**: The app now uses `socketio.run()` instead of `app.run()` for WebSocket support.

## 🎯 Event Triggers

The system automatically sends notifications when these events occur:

### User Registration
- **Trigger**: New user signs up
- **Message**: "New user {name} ({email}) has registered on the platform."
- **Type**: `info`

### User Login
- **Trigger**: User logs in
- **Message**: "User {name} ({email}) has logged in."
- **Type**: `info`

### Feedback Submission
- **Trigger**: User submits feedback
- **Message**: "User {name} has submitted new feedback with {rating}/5 rating. Sentiment: {sentiment} (score: {score})"
- **Type**: `info`

### Profile Update
- **Trigger**: User updates profile information
- **Message**: "User {name} ({email}) has updated their profile."
- **Type**: `info`

## 🔌 WebSocket Events

### Client → Server
- `connect` - Establish connection
- `join_admin_room` - Join admin notification room
- `leave_admin_room` - Leave admin notification room

### Server → Client
- `new_notification` - New notification received
- `connection_status` - Connection status update
- `room_joined` - Room join confirmation

## 📡 API Endpoints

### GET `/api/notifications/count`
Get unread notification count for current user's role.

**Response:**
```json
{
  "is_admin": true,
  "unread_count": 5
}
```

### GET `/api/notifications?limit=10`
Get recent notifications for current user's role.

**Response:**
```json
{
  "notifications": [
    {
      "id": 1,
      "message": "New user John Doe has registered",
      "type": "info",
      "timestamp": "2025-01-15T10:30:00Z",
      "read": false,
      "user_id": 123,
      "event_data": {"email": "john@example.com", "name": "John Doe"}
    }
  ],
  "total": 1
}
```

### POST `/api/notifications/{id}/read`
Mark a specific notification as read.

**Response:**
```json
{
  "message": "Notification marked as read"
}
```

## 🎨 Frontend Components

### Notification Dropdown
- **Location**: Navbar (admin users only)
- **Features**: 
  - Unread count badge
  - Real-time updates
  - Click to mark as read
  - Color-coded notification types
  - Timestamp display

### Real-time Updates
- **WebSocket Connection**: Automatic on admin login
- **Instant Updates**: No page refresh required
- **Toast Notifications**: Pop-up alerts for new notifications
- **Badge Updates**: Real-time count changes

## 🛠️ Adding New Event Triggers

To add notifications for new events, use the notification service:

```python
from app.services.notification_service import send_admin_notification

# Send a simple notification
send_admin_notification(
    message="Something important happened!",
    type="warning"
)

# Send with user context and event data
send_admin_notification(
    message="User {name} performed action X",
    type="info",
    user_id=user.id,
    event_data={"action": "action_x", "details": "more info"}
)
```

### Notification Types
- `success` - Green styling, positive events
- `info` - Blue styling, informational events  
- `warning` - Yellow styling, cautionary events
- `error` - Red styling, error events

## 🧪 Testing

### Run the Test Script
```bash
python test_notifications.py
```

### Manual Testing
1. **Start the app**: `python run.py`
2. **Login as admin**: Use admin@example.com / AdminPass123!
3. **Check navbar**: Look for notification bell with dropdown
4. **Trigger events**: Register users, submit feedback, etc.
5. **Watch real-time**: Notifications appear instantly via WebSocket

### Browser Console
Check for WebSocket connection logs:
```
Connected to Socket.IO server
Room joined: {"room": "role_admin", "status": "success"}
New notification received: {...}
```

## 🔒 Security Features

- **Role-based access**: Only admin users receive notifications
- **JWT authentication**: Secure WebSocket connections
- **Room isolation**: Users only join their role-specific rooms
- **Input validation**: Sanitized notification content

## 🚨 Troubleshooting

### Common Issues

1. **Notifications not showing**
   - Check user role is 'admin'
   - Verify WebSocket connection in browser console
   - Check database for notification records

2. **WebSocket connection failed**
   - Ensure app is running with `python run.py`
   - Check firewall/network settings
   - Verify Socket.IO client library is loaded

3. **Real-time updates not working**
   - Check browser console for errors
   - Verify user is in correct Socket.IO room
   - Check notification service is emitting events

### Debug Mode
Enable debug logging in the notification service:
```python
# In app/services/notification_service.py
print(f"Emitting notification: {data}")
```

## 📈 Performance Considerations

- **Database indexing**: `recipient_role` and `read` columns are indexed
- **WebSocket rooms**: Efficient message delivery to specific user groups
- **Lazy loading**: Notifications loaded on-demand
- **Connection pooling**: Socket.IO handles multiple concurrent connections

## 🔮 Future Enhancements

- **Email notifications** for critical events
- **Push notifications** for mobile devices
- **Notification preferences** (frequency, types)
- **Bulk operations** (mark all read, delete old)
- **Notification templates** with rich formatting
- **Analytics dashboard** for notification metrics

## 📚 Dependencies

- `Flask-SocketIO==5.3.6` - WebSocket support
- `python-socketio==5.10.0` - Socket.IO implementation
- `Flask-SQLAlchemy==3.1.1` - Database ORM
- `Bootstrap 5.3.0` - Frontend styling
- `Socket.IO Client 4.7.2` - Frontend WebSocket library

## 🤝 Contributing

When adding new notification types or events:

1. Update the notification model if needed
2. Add event triggers in relevant routes
3. Test WebSocket delivery
4. Update this documentation
5. Add appropriate tests

---

**Note**: This system is designed to be non-intrusive and only affects admin users. Regular users will not see any notification UI elements or receive WebSocket messages.
