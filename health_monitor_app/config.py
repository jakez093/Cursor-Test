"""
Configuration settings for the Health Monitor application.

This module contains configuration classes for different environments:
- Development: For local development with debugging enabled
- Testing: For running automated tests
- Production: For deployment with enhanced security
"""
import os
from datetime import timedelta

class Config:
    """Base config class with settings common to all environments."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-for-testing-replace-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    REMEMBER_COOKIE_DURATION = timedelta(days=14)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = False  # Set to True in production
    
    # Session settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # Set to True in production
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
    }


class DevelopmentConfig(Config):
    """Development environment config with debug enabled."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///health_data.db')
    

class TestingConfig(Config):
    """Testing environment config with testing database."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing


class ProductionConfig(Config):
    """Production environment config with enhanced security."""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///health_data.db')
    
    # Enhanced security settings for production
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    
    # Set more restrictive SameSite policy
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # Add secure flag to session/cookies
    # These should be set to True only if using HTTPS
    WTF_CSRF_SSL_STRICT = True 