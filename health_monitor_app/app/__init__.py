"""
Application factory module for the Health Monitor application.

This module contains the application factory that creates a Flask app
instance and registers all necessary configurations and blueprints.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask

from .extensions import db, login

def create_app(test_config=None):
    """
    Create and configure a Flask application instance.
    
    Args:
        test_config: Configuration dict for testing (optional)
        
    Returns:
        Flask application instance
    """
    # Create Flask app instance
    app = Flask(__name__, instance_relative_config=True)
    
    # Load default configuration
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'health_monitor.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Load test configuration if provided
    if test_config is not None:
        app.config.from_mapping(test_config)
    
    # Initialize extensions with app
    db.init_app(app)
    login.init_app(app)
    
    # Ensure database tables exist
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.error(f"Error creating database tables: {e}")
    
    # Register blueprints
    # Import and register the auth blueprint first
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from .health_data import health_data as health_data_blueprint
    app.register_blueprint(health_data_blueprint, url_prefix='/health')
    
    # Register main routes
    from . import routes
    app.register_blueprint(routes.main)
    
    # Setup logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/health_monitor.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Health Monitor startup')
        
    return app 