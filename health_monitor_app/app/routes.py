"""
Main routes for the Health Monitor application.

This module defines the main routes for the application, including the home page.
"""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

# Create blueprint
main = Blueprint('main', __name__)

@main.route('/')
def index():
    """
    Render the home page.
    
    If user is authenticated, redirect to dashboard. Otherwise show landing page.
    """
    if current_user.is_authenticated:
        return redirect(url_for('health_data.dashboard'))
    return render_template('main/landing.html')

@main.route('/dashboard')
def dashboard():
    """Redirect to the health data dashboard."""
    return redirect(url_for('health_data.dashboard')) 