"""
Health data blueprint for the Health Monitor application.
This module handles all routes related to health data management.
"""
from flask import Blueprint

health_data = Blueprint('health_data', __name__, url_prefix='/health')

# Import routes after creating the Blueprint to avoid circular imports
from . import routes
