"""
Flask extensions for the Health Monitor application.

This module initializes all Flask extensions used by the application.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize extensions
db = SQLAlchemy()
login = LoginManager()

# Configure extensions - ensure these match blueprint endpoint names exactly
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'
login.login_message_category = 'info' 