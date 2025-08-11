#!/usr/bin/env python3
"""
WSGI entry point for the Flask application
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set Flask environment
os.environ.setdefault('FLASK_ENV', 'production')

from app import create_app

# Create application instance
app = create_app()

if __name__ == '__main__':
    app.run()
