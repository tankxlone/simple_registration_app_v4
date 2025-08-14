#!/usr/bin/env python3
"""
Test JWT functionality and authentication
"""
import requests
import json

BASE_URL = "http://localhost:5000"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "AdminPass123!"

def test_jwt_authentication():
    """Test JWT authentication flow"""
    print("🔐 Testing JWT Authentication")
    print("=" * 40)
    
    session = requests.Session()
    
    # Step 1: Login
    print("\n1. Logging in...")
    login_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    login_response = session.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"   Status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        print("✅ Login successful")
        
        # Check cookies
        cookies = login_response.cookies
        print(f"   Cookies: {list(cookies.keys())}")
        
        for cookie_name, cookie_value in cookies.items():
            print(f"   {cookie_name}: {cookie_value[:20]}...")
        
        # Step 2: Test protected endpoint
        print("\n2. Testing protected endpoint...")
        
        # Try to access a protected endpoint
        protected_response = session.get(f"{BASE_URL}/api/notifications/count")
        print(f"   Status: {protected_response.status_code}")
        print(f"   Response: {protected_response.text[:200]}")
        
        # Step 3: Test with explicit cookie header
        print("\n3. Testing with explicit cookie header...")
        
        # Get the access token from cookies
        access_token = cookies.get('access_token_cookie')
        if access_token:
            print(f"   Access token found: {access_token[:20]}...")
            
            # Try with Authorization header
            headers = {'Authorization': f'Bearer {access_token}'}
            auth_response = session.get(f"{BASE_URL}/api/notifications/count", headers=headers)
            print(f"   Status with Authorization header: {auth_response.status_code}")
            print(f"   Response: {auth_response.text[:200]}")
        else:
            print("   ❌ No access token cookie found")
            
    else:
        print(f"❌ Login failed: {login_response.text}")
    
    return True

def test_cookie_handling():
    """Test how cookies are handled"""
    print("\n🍪 Testing Cookie Handling")
    print("=" * 30)
    
    session = requests.Session()
    
    # Login first
    login_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    login_response = session.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if login_response.status_code == 200:
        print("✅ Login successful")
        
        # Check if cookies are in session
        print(f"   Session cookies: {list(session.cookies.keys())}")
        
        # Try to access protected endpoint
        response = session.get(f"{BASE_URL}/api/notifications/count")
        print(f"   Protected endpoint status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
        # Check if cookies are being sent
        print(f"   Request cookies: {dict(session.cookies)}")
        
    else:
        print(f"❌ Login failed: {login_response.status_code}")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting JWT Authentication Tests")
    print()
    
    test_jwt_authentication()
    test_cookie_handling()
    
    print("\n📋 Test Summary:")
    print("- Check if JWT tokens are being set correctly")
    print("- Verify cookie handling in requests")
    print("- Debug authentication flow")
