# Secure Flask Feedback Application

A production-ready Flask web application with Bootstrap UI that provides secure user authentication, role-based access control, and AI-powered sentiment analysis for feedback management.

## 🚀 Features

### Core Functionality

- **Secure Authentication**: JWT-based login/registration with password hashing (bcrypt)
- **Role-Based Access Control**: User and admin roles with different permissions
- **User Profile Management**: Update names and upload avatars with validation
- **Feedback System**: Submit feedback with real-time sentiment analysis
- **Admin Dashboard**: Comprehensive user and feedback management
- **Real-Time Sentiment Preview**: Instant sentiment analysis without storing data

### Security Features

- **HTTPS-ready cookies** for refresh tokens (HttpOnly, Secure, SameSite=Lax)
- **CSRF protection** for all forms
- **Rate limiting** on authentication endpoints
- **Input sanitization** and validation
- **Token revocation** for secure logout
- **Password strength requirements** (8+ chars, uppercase, lowercase, number, special char)

### Technical Features

- **Database**: SQLAlchemy + Flask-Migrate (PostgreSQL production, SQLite development)
- **Frontend**: Responsive Bootstrap 5 with accessibility features
- **Client-side validation** with server-side enforcement
- **File upload validation** (JPG, PNG, max 2MB)
- **Sentiment Analysis**: VADER (default) + Hugging Face Transformers support
- **Docker support** with docker-compose for local development

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.11+
- PostgreSQL (for production) or SQLite (for development)
- Docker and Docker Compose (optional)

### Option 1: Local Development

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd simple_registration_v5
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database (Choose one method)**

   **Method A: Simple initialization script (Recommended)**

   ```bash
   python init_db.py
   ```

   **Method B: Flask CLI commands**

   ```bash
   python -m flask init-db
   python -m flask create-admin
   ```

   **Method C: Direct Python script**

   ```bash
   python manage.py init-db
   python manage.py create-admin
   ```

6. **Run the application**

   ```bash
   # Option 1: Using the run script
   python run.py

   # Option 2: Using Flask CLI
   python -m flask run

   # Option 3: Using manage.py
   python manage.py run
   ```

### Option 2: Docker Development

1. **Clone and navigate to project**

   ```bash
   git clone <repository-url>
   cd simple_registration_v5
   ```

2. **Start services**

   ```bash
   docker-compose up --build
   ```

3. **Initialize database** (in another terminal)

   ```bash
   docker-compose exec app python init_db.py
   ```

4. **Access the application**
   - Flask App: http://localhost:8000
   - PostgreSQL: localhost:5432
   - Redis: localhost:6379
   - Nginx: http://localhost:80

## 🧪 Testing

Run the test suite:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest --cov=app tests/
```

## 📁 Project Structure

```
simple_registration_v5/
├── app/                          # Application package
│   ├── __init__.py              # App factory
│   ├── models.py                 # Database models
│   ├── forms.py                  # Flask-WTF forms
│   ├── auth/                     # Authentication blueprint
│   ├── main/                     # Main routes blueprint
│   ├── profile/                  # Profile management blueprint
│   ├── feedback/                 # Feedback system blueprint
│   ├── admin/                    # Admin dashboard blueprint
│   ├── api/                      # API endpoints blueprint
│   ├── services/                 # Business logic services
│   ├── static/                   # Static files (CSS, JS, uploads)
│   └── templates/                # HTML templates
├── tests/                        # Test suite
├── config.py                     # Configuration classes
├── requirements.txt              # Python dependencies
├── manage.py                     # Flask CLI management script
├── init_db.py                    # Database initialization script
├── run.py                        # Simple run script
├── Dockerfile                    # Production Docker image
├── docker-compose.yml            # Local development setup
├── wsgi.py                       # Production WSGI entry point
└── README.md                     # This file
```

## 🔧 Configuration

### Environment Variables

| Variable            | Description                | Default                                   |
| ------------------- | -------------------------- | ----------------------------------------- |
| `FLASK_ENV`         | Flask environment          | `development`                             |
| `SECRET_KEY`        | Flask secret key           | `dev-secret-key-change-in-production`     |
| `JWT_SECRET_KEY`    | JWT secret key             | `dev-jwt-secret-key-change-in-production` |
| `DATABASE_URL`      | Database connection string | `sqlite:///app.db`                        |
| `SENTIMENT_SERVICE` | Sentiment analysis service | `vader`                                   |

### Database Configuration

**Development (SQLite):**

```bash
DATABASE_URL=sqlite:///app.db
```

**Production (PostgreSQL):**

```bash
DATABASE_URL=postgresql://username:password@host:port/database
```

## 🚀 Deployment

### Production with Gunicorn + Nginx

1. **Build Docker image**

   ```bash
   docker build -t feedback-app .
   ```

2. **Run with Gunicorn**

   ```bash
   docker run -p 8000:8000 \
     -e FLASK_ENV=production \
     -e DATABASE_URL=your-postgres-url \
     -e SECRET_KEY=your-secret-key \
     feedback-app
   ```

3. **Nginx configuration**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Environment-Specific Configs

The application automatically detects the environment and applies appropriate settings:

- **Development**: Debug mode, SQLite, HTTP cookies
- **Production**: Production mode, PostgreSQL, HTTPS cookies, CSRF enabled
- **Testing**: Test database, CSRF disabled

## 🔐 Security Features

### Authentication & Authorization

- JWT tokens with configurable expiration
- Secure HTTP-only cookies for refresh tokens
- Role-based access control (user/admin)
- Password strength validation
- Rate limiting on auth endpoints

### Data Protection

- Input sanitization and validation
- CSRF protection for forms
- File upload validation and sanitization
- SQL injection prevention via SQLAlchemy
- XSS protection through proper escaping

### Session Management

- Token-based authentication
- Automatic token refresh
- Secure logout with token revocation
- Session timeout configuration

## 📊 API Endpoints

### Authentication

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user info

### Feedback

- `GET /feedback/submit` - Feedback submission form
- `POST /feedback/submit` - Submit feedback
- `GET /feedback/my-feedback` - User's feedback history
- `GET /feedback/<id>` - View specific feedback

### Admin

- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/users` - Manage users
- `GET /admin/feedback` - Manage feedback
- `POST /admin/feedback/<id>/correct` - Correct sentiment
- `GET /admin/export/feedback.csv` - Export feedback data

### API

- `POST /api/feedback/preview` - Real-time sentiment preview
- `GET /api/feedback/stats` - User feedback statistics
- `GET /api/admin/stats` - Admin statistics
- `GET /api/health` - Health check

## 🎨 Frontend Features

### Bootstrap 5 UI

- Responsive design for all devices
- Modern card-based layouts
- Interactive form validation
- Toast notifications
- Modal dialogs

### Accessibility

- ARIA labels and descriptions
- Keyboard navigation support
- Screen reader compatibility
- High contrast support
- Focus management

### JavaScript Features

- Real-time form validation
- Sentiment preview with debouncing
- AJAX form submissions
- Dynamic content loading
- Error handling and user feedback

## 🔍 Sentiment Analysis

### VADER (Default)

- Fast and lightweight
- Good for social media text
- Configurable banned words
- Real-time analysis

### Hugging Face Transformers

- State-of-the-art accuracy
- Multiple model options
- GPU acceleration support
- Easy model switching

### Configuration

```python
# Switch sentiment service
SENTIMENT_SERVICE=huggingface  # or 'vader'

# Customize banned words
BANNED_WORDS = ['spam', 'scam', 'fake', 'hate']
```

## 📈 Monitoring & Logging

### Health Checks

- Database connectivity
- Service availability
- Response time monitoring

### Logging

- Structured logging with levels
- Error tracking and reporting
- Performance metrics
- Security event logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Check the documentation
- Review the test examples

## 🔄 Updates & Maintenance

### Regular Maintenance

- Update dependencies monthly
- Security patches as needed
- Database migrations
- Performance monitoring

### Version Compatibility

- Python: 3.11+
- Flask: 3.0+
- PostgreSQL: 12+
- Docker: 20.10+

## 🚨 Troubleshooting

### Common Issues

**"No such command 'db'" error:**

- Use `python init_db.py` instead of Flask-Migrate commands
- Or use the custom CLI commands: `python -m flask init-db`

**Database connection issues:**

- Check your `.env` file configuration
- Ensure SQLite file permissions (for development)
- Verify PostgreSQL connection (for production)

**Import errors:**

- Make sure you're in the project root directory
- Activate your virtual environment
- Check that all dependencies are installed

---

**Built with ❤️ using Flask, Bootstrap, and modern web technologies**
