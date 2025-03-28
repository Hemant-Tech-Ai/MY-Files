import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///quiz_master.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)  # Increase to 24 hours for development
    JWT_HEADER_TYPE = 'Bearer'  # Ensure this matches what we send from the frontend
    
    # Additional JWT settings
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    
    # Fix for subject type validation
    JWT_IDENTITY_CLAIM = 'sub'
    
    # Email configuration
    SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
    FROM_EMAIL = os.environ.get('FROM_EMAIL', 'quizmaster@example.com')
    EMAIL_DEBUG_MODE = os.environ.get('EMAIL_DEBUG_MODE', 'True') == 'True'
    
    # Caching configuration
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')  # simple, redis, etc.
    CACHE_REDIS_URL = os.environ.get('CACHE_REDIS_URL', '')
    CACHE_TIMEOUT = int(os.environ.get('CACHE_TIMEOUT', '300'))
    ENABLE_CACHING = os.environ.get('ENABLE_CACHING', 'True') == 'True'
    
    # Flask-APScheduler settings
    SCHEDULER_API_ENABLED = False
    SCHEDULER_TIMEZONE = 'UTC'