"""
Main routes for the Health Monitor application.

This module defines the main routes for the application, including the home page.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from .extensions import db

# Create blueprint
main = Blueprint('main', __name__)

@main.route('/')
def index():
    """
    Render the home page.
    
    If user is authenticated, redirect to dashboard. Otherwise show landing page.
    """
    if current_user.is_authenticated:
        return redirect(url_for('health_data.history'))
    return render_template('main/landing.html')

@main.route('/dashboard')
def dashboard():
    """Redirect to the health data dashboard."""
    return redirect(url_for('health_data.history'))

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    User profile page.
    """
    return render_template('main/profile.html', title='User Profile')
    
@main.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """
    User settings page.
    """
    return render_template('main/settings.html', title='User Settings')
