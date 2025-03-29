"""
Authentication blueprint for the Health Monitor application.
This module handles user authentication, including login, registration, and logout.
"""
from flask import Blueprint

# Create blueprint with explicit name matching login.login_view setting
auth = Blueprint('auth', __name__)

from . import routes
