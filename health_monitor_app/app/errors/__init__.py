"""
Error handlers blueprint for the Health Monitor application.

This module provides a blueprint for handling various HTTP errors and 
custom error pages.
"""
from flask import Blueprint

errors = Blueprint('errors', __name__)

from . import handlers 