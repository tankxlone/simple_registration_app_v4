import pytest
from app import create_app, db
from app.models import User, TokenBlocklist
from app.services.sentiment_service import get_sentiment_service
import json

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test runner"""
    return app.test_cli_runner()

class TestAuthentication:
    """Test authentication functionality"""
    
    def test_user_registration_success(self, client):
        """Test successful user registration"""
        data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!',
            'name': 'Test User'
        }
        
        response = client.post('/auth/register',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'message' in data
        assert data['message'] == 'Registration successful'
        assert 'user' in data
        assert data['user']['email'] == 'test@example.com'
        assert data['user']['name'] == 'Test User'
        assert data['user']['role'] == 'user'
    
    def test_user_registration_duplicate_email(self, client):
        """Test registration with duplicate email"""
        # First registration
        data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!',
            'name': 'Test User'
        }
        client.post('/auth/register',
                   data=json.dumps(data),
                   content_type='application/json')
        
        # Second registration with same email
        response = client.post('/auth/register',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'errors' in data
        assert 'email' in data['errors']
        assert 'already registered' in data['errors']['email']
    
    def test_user_registration_invalid_password(self, client):
        """Test registration with invalid password"""
        data = {
            'email': 'test@example.com',
            'password': 'weak',
            'confirm_password': 'weak',
            'name': 'Test User'
        }
        
        response = client.post('/auth/register',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'errors' in data
        assert 'password' in data['errors']
    
    def test_user_registration_password_mismatch(self, client):
        """Test registration with password mismatch"""
        data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'confirm_password': 'DifferentPass123!',
            'name': 'Test User'
        }
        
        response = client.post('/auth/register',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'errors' in data
        assert 'confirm_password' in data['errors']
        assert 'do not match' in data['errors']['confirm_password']
    
    def test_user_login_success(self, client):
        """Test successful user login"""
        # First register a user
        reg_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!',
            'name': 'Test User'
        }
        client.post('/auth/register',
                   data=json.dumps(reg_data),
                   content_type='application/json')
        
        # Then login
        login_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        }
        
        response = client.post('/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        assert data['message'] == 'Login successful'
        assert 'user' in data
        assert data['user']['email'] == 'test@example.com'
    
    def test_user_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        data = {
            'email': 'test@example.com',
            'password': 'WrongPassword123!'
        }
        
        response = client.post('/auth/login',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Invalid email or password' in data['error']
    
    def test_user_logout(self, client):
        """Test user logout"""
        # First register and login to get tokens
        reg_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!',
            'name': 'Test User'
        }
        client.post('/auth/register',
                   data=json.dumps(reg_data),
                   content_type='application/json')
        
        login_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        }
        login_response = client.post('/auth/login',
                                   data=json.dumps(login_data),
                                   content_type='application/json')
        
        # Extract cookies for logout
        cookies = login_response.headers.getlist('Set-Cookie')
        
        # Test logout
        response = client.post('/auth/logout',
                             headers={'Cookie': '; '.join(cookies)})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        assert data['message'] == 'Logout successful'

class TestUserValidation:
    """Test user input validation"""
    
    def test_email_validation(self):
        """Test email format validation"""
        valid_emails = [
            'test@example.com',
            'user.name@domain.co.uk',
            'user+tag@example.org'
        ]
        
        invalid_emails = [
            'invalid-email',
            '@example.com',
            'user@',
            'user.example.com'
        ]
        
        for email in valid_emails:
            assert User.validate_email(email) is True
        
        for email in invalid_emails:
            assert User.validate_email(email) is False
    
    def test_password_validation(self):
        """Test password strength validation"""
        valid_password = 'TestPass123!'
        is_valid, message = User.validate_password(valid_password)
        assert is_valid is True
        assert message == 'Password is valid'
        
        # Test weak passwords
        weak_passwords = [
            'short',  # Too short
            'nouppercase123!',  # No uppercase
            'NOLOWERCASE123!',  # No lowercase
            'NoNumbers!',  # No numbers
            'NoSpecial123'  # No special characters
        ]
        
        for password in weak_passwords:
            is_valid, message = User.validate_password(password)
            assert is_valid is False
            assert len(message) > 0
    
    def test_name_validation(self):
        """Test name format validation"""
        valid_names = [
            'John Doe',
            'Mary',
            'Jean-Pierre'
        ]
        
        invalid_names = [
            'A',  # Too short
            'This name is way too long and exceeds the maximum allowed length',  # Too long
            'John123',  # Contains numbers
            'Mary@Doe',  # Contains special characters
            ''  # Empty
        ]
        
        for name in valid_names:
            is_valid, message = User.validate_name(name)
            assert is_valid is True
            assert message == 'Name is valid'
        
        for name in invalid_names:
            is_valid, message = User.validate_name(name)
            assert is_valid is False
            assert len(message) > 0

class TestSentimentService:
    """Test sentiment analysis service"""
    
    def test_vader_sentiment_analysis(self):
        """Test VADER sentiment analysis"""
        service = get_sentiment_service('vader')
        
        # Test positive sentiment
        label, confidence, analysis = service.analyze_sentiment(
            "I absolutely love this product! It's amazing and works perfectly."
        )
        assert label == 'positive'
        assert confidence > 0.5
        assert 'banned_words_detected' in analysis
        
        # Test negative sentiment
        label, confidence, analysis = service.analyze_sentiment(
            "This is terrible. I hate it and it doesn't work at all."
        )
        assert label == 'negative'
        assert confidence > 0.5
        
        # Test neutral sentiment
        label, confidence, analysis = service.analyze_sentiment(
            "The product is okay. It works but nothing special."
        )
        assert label == 'neutral'
    
    def test_banned_words_detection(self):
        """Test banned words detection"""
        service = get_sentiment_service('vader')
        
        # Test with banned word
        label, confidence, analysis = service.analyze_sentiment(
            "This is spam and fake content"
        )
        assert label == 'negative'
        assert confidence == 1.0
        assert analysis['banned_words_detected'] is True
        
        # Test without banned words
        label, confidence, analysis = service.analyze_sentiment(
            "This is a great product"
        )
        assert analysis['banned_words_detected'] is False
