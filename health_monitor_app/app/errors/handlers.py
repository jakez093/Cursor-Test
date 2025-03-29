"""
Error handlers for the Health Monitor application.

This module defines handlers for various HTTP errors, providing 
user-friendly error pages and appropriate logging.
"""
from flask import render_template, request, current_app
from werkzeug.http import HTTP_STATUS_CODES
from sqlalchemy.exc import SQLAlchemyError

from ..extensions import db
from . import errors


@errors.app_errorhandler(404)
def not_found_error(error):
    """Handle 404 Not Found errors."""
    return render_template('errors/404.html', 
                           title='Page Not Found'), 404


@errors.app_errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server Error."""
    # Rollback any failed database transactions
    db.session.rollback()
    
    # Log the error
    current_app.logger.error(f"Internal server error: {str(error)}")
    current_app.logger.error(f"Request path: {request.path}")
    
    return render_template('errors/500.html', 
                           title='Internal Server Error'), 500


@errors.app_errorhandler(403)
def forbidden_error(error):
    """Handle 403 Forbidden errors."""
    return render_template('errors/403.html', 
                           title='Access Forbidden'), 403


@errors.app_errorhandler(401)
def unauthorized_error(error):
    """Handle 401 Unauthorized errors."""
    return render_template('errors/401.html', 
                           title='Unauthorized'), 401


@errors.app_errorhandler(400)
def bad_request_error(error):
    """Handle 400 Bad Request errors."""
    return render_template('errors/400.html', 
                           title='Bad Request'), 400


@errors.app_errorhandler(SQLAlchemyError)
def database_error(error):
    """Handle database errors."""
    db.session.rollback()
    
    # Log the error
    current_app.logger.error(f"Database error: {str(error)}")
    current_app.logger.error(f"Request path: {request.path}")
    
    return render_template('errors/500.html', 
                           title='Database Error'), 500


@errors.app_errorhandler(Exception)
def unhandled_exception(error):
    """Handle any unhandled exceptions."""
    db.session.rollback()
    
    # Log the error in detail
    current_app.logger.error(f"Unhandled exception: {str(error)}")
    current_app.logger.error(f"Request path: {request.path}")
    current_app.logger.exception(error)
    
    return render_template('errors/500.html', 
                           title='Unexpected Error'), 500 