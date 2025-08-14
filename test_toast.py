#!/usr/bin/env python3
"""
Test toast notification functionality and WebSocket events
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "AdminPass123!"

def test_toast_notifications():
    """Test toast notification functionality"""
    print("🍞 Testing Toast Notifications")
    print("=" * 40)
    
    # Step 1: Login as admin
    print("\n1. Logging in as admin...")
    session = requests.Session()
    login_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    login_response = session.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    print("✅ Admin login successful")
    
    # Step 2: Create a test notification to trigger WebSocket event
    print("\n2. Creating test notification...")
    
    try:
        from app import create_app, db
        from app.services.notification_service import send_admin_notification
        
        app = create_app()
        with app.app_context():
            # Create a test notification that should trigger WebSocket event
            notification = send_admin_notification(
                message="🎉 Toast test notification! This should trigger a toast!",
                type="success",
                event_data={"test": True, "toast_test": True, "timestamp": str(time.time())}
            )
            
            if notification:
                print("✅ Test notification created successfully")
                print(f"   ID: {notification.id}")
                print(f"   Message: {notification.message}")
                print(f"   Type: {notification.type}")
                print("\n   🔔 This notification should have triggered a WebSocket event")
                print("   📱 Check your browser for a toast notification!")
            else:
                print("❌ Failed to create test notification")
                
    except Exception as e:
        print(f"❌ Error creating test notification: {e}")
    
    # Step 3: Test the notification service directly
    print("\n3. Testing notification service...")
    
    try:
        from app import create_app, db
        from app.services.notification_service import send_admin_notification
        
        app = create_app()
        with app.app_context():
            # Test different notification types
            notifications = [
                ("success", "🎯 Success notification - should show green toast"),
                ("info", "ℹ️ Info notification - should show blue toast"),
                ("warning", "⚠️ Warning notification - should show yellow toast"),
                ("error", "❌ Error notification - should show red toast")
            ]
            
            for notification_type, message in notifications:
                notification = send_admin_notification(
                    message=message,
                    type=notification_type,
                    event_data={"test": True, "type": notification_type}
                )
                
                if notification:
                    print(f"   ✅ Created {notification_type} notification: {notification.id}")
                else:
                    print(f"   ❌ Failed to create {notification_type} notification")
                    
    except Exception as e:
        print(f"❌ Error testing notification service: {e}")
    
    print("\n" + "=" * 40)
    print("🎉 Toast notification test completed!")
    print("\n📋 What to check:")
    print("- Open your browser and login as admin")
    print("- Look for toast notifications appearing in the top-right corner")
    print("- Check browser console for WebSocket connection logs")
    print("- Each notification type should have different colors")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Toast Notification Tests")
    print("Make sure the Flask app is running with: python run.py")
    print()
    
    test_toast_notifications()
