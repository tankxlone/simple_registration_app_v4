#!/usr/bin/env python3
"""
Test script to verify the notification system is working
"""
import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "AdminPass123!"

def test_notification_system():
    """Test the notification system end-to-end"""
    print("🧪 Testing Notification System")
    print("=" * 50)
    
    # Step 1: Login as admin
    print("\n1. Logging in as admin...")
    login_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    session = requests.Session()
    login_response = session.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return False
    
    print("✅ Admin login successful")
    
    # Extract cookies from login response
    cookies = login_response.cookies
    print(f"   Cookies received: {list(cookies.keys())}")
    
    # Step 2: Check notification count
    print("\n2. Checking notification count...")
    count_response = session.get(f"{BASE_URL}/api/notifications/count")
    
    if count_response.status_code == 200:
        count_data = count_response.json()
        print(f"✅ Notification count: {count_data.get('unread_count', 0)}")
        print(f"   Is admin: {count_data.get('is_admin', False)}")
    else:
        print(f"❌ Failed to get notification count: {count_response.status_code}")
        print(f"   Response: {count_response.text}")
    
    # Step 3: Get notifications list
    print("\n3. Getting notifications list...")
    notifications_response = session.get(f"{BASE_URL}/api/notifications?limit=5")
    
    if notifications_response.status_code == 200:
        notifications_data = notifications_response.json()
        print(f"✅ Found {len(notifications_data.get('notifications', []))} notifications")
        
        # Display recent notifications
        for i, notification in enumerate(notifications_data.get('notifications', [])[:3]):
            print(f"   {i+1}. [{notification.get('type', 'unknown')}] {notification.get('message', 'No message')}")
            print(f"      Read: {notification.get('read', False)}, Time: {notification.get('timestamp', 'Unknown')}")
    else:
        print(f"❌ Failed to get notifications: {notifications_response.status_code}")
        print(f"   Response: {notifications_response.text}")
    
    # Step 4: Test marking notification as read (if there are notifications)
    if notifications_response.status_code == 200:
        notifications_data = notifications_response.json()
        notifications = notifications_data.get('notifications', [])
        
        if notifications:
            first_notification = notifications[0]
            notification_id = first_notification.get('id')
            
            if notification_id and not first_notification.get('read', True):
                print(f"\n4. Marking notification {notification_id} as read...")
                mark_read_response = session.post(f"{BASE_URL}/api/notifications/{notification_id}/read")
                
                if mark_read_response.status_code == 200:
                    print("✅ Notification marked as read")
                else:
                    print(f"❌ Failed to mark notification as read: {mark_read_response.status_code}")
                    print(f"   Response: {mark_read_response.text}")
            else:
                print("\n4. Skipping mark as read test (no unread notifications)")
        else:
            print("\n4. Skipping mark as read test (no notifications)")
    
    print("\n" + "=" * 50)
    print("🎉 Notification system test completed!")
    
    return True

def test_websocket_connection():
    """Test WebSocket connection (basic check)"""
    print("\n🔌 Testing WebSocket Connection")
    print("=" * 30)
    
    try:
        # Check if the server is running with SocketIO
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Server is running")
            
            # Check if Socket.IO client library is loaded in the response
            if "socket.io" in response.text.lower():
                print("✅ Socket.IO client library detected in HTML")
            else:
                print("⚠️  Socket.IO client library not found in HTML")
        else:
            print(f"❌ Server not responding: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running with: python run.py")
        return False
    
    return True

def test_simple_notification_creation():
    """Test creating a simple notification directly"""
    print("\n🔔 Testing Direct Notification Creation")
    print("=" * 40)
    
    try:
        from app import create_app, db
        from app.services.notification_service import send_admin_notification
        
        app = create_app()
        with app.app_context():
            # Create a test notification
            notification = send_admin_notification(
                message="Test notification from test script",
                type="info",
                event_data={"test": True, "timestamp": str(time.time())}
            )
            
            if notification:
                print("✅ Test notification created successfully")
                print(f"   ID: {notification.id}")
                print(f"   Message: {notification.message}")
                print(f"   Type: {notification.type}")
            else:
                print("❌ Failed to create test notification")
                
    except Exception as e:
        print(f"❌ Error creating test notification: {e}")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Notification System Tests")
    print("Make sure the Flask app is running with: python run.py")
    print()
    
    # Test WebSocket setup
    test_websocket_connection()
    
    # Test direct notification creation
    test_simple_notification_creation()
    
    # Test notification API
    test_notification_system()
    
    print("\n📋 Test Summary:")
    print("- Check the browser console for WebSocket connection logs")
    print("- Look for the notification dropdown in the navbar (admin users only)")
    print("- Try triggering events (register user, submit feedback, etc.)")
    print("- Notifications should appear in real-time via WebSocket")
