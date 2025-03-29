"""
Main blueprint for the Health Monitor application.
This module handles the main routes, including the dashboard.
"""
from flask import Blueprint

main = Blueprint('main', __name__)

from . import routes 