"""
Security module for the Health Monitor application.

This module contains utilities to enhance security, including:
- Input sanitization and validation
- Protection against common web vulnerabilities
- Security headers and configurations
"""
import re
import bleach
from functools import wraps
from flask import request, abort, make_response, current_app
from werkzeug.urls import url_parse
from typing import Callable, Any, Dict, List, Optional, Union

# Allowed HTML tags and attributes for text sanitization
ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li', 'span']
ALLOWED_ATTRIBUTES = {
    '*': ['class', 'style'],
    'a': ['href', 'title', 'target'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
}

def sanitize_input(text: Optional[str]) -> Optional[str]:
    """
    Sanitize user input to prevent XSS attacks.
    
    Args:
        text: The input text to sanitize
        
    Returns:
        Sanitized text with potentially harmful content removed
    """
    if text is None:
        return None
    
    # First strip any null bytes (can be used in SQL injection)
    text = text.replace('\0', '')
    
    # Sanitize HTML content
    return bleach.clean(
        text,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )

def sanitize_form_data(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize all string values in form data.
    
    Args:
        form_data: Dictionary containing form data
        
    Returns:
        Dictionary with sanitized values
    """
    sanitized_data = {}
    for key, value in form_data.items():
        if isinstance(value, str):
            sanitized_data[key] = sanitize_input(value)
        else:
            sanitized_data[key] = value
    return sanitized_data

def validate_url_safe(url: str) -> bool:
    """
    Validate that a URL is safe and doesn't contain protocol-relative links.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is safe, False otherwise
    """
    parsed_url = url_parse(url)
    return parsed_url.netloc == ''

def add_security_headers(response):
    """
    Add security headers to a response.
    
    Args:
        response: Flask response object
        
    Returns:
        Response with added security headers
    """
    # Add headers from configuration
    for header, value in current_app.config.get('SECURITY_HEADERS', {}).items():
        if header not in response.headers:
            response.headers[header] = value
    
    return response

def apply_rate_limit(key: str, max_requests: int, period: int) -> bool:
    """
    Simple in-memory rate limiting.
    
    This is a placeholder for a more robust implementation.
    In production, use a proper rate limiting solution with Redis.
    
    Args:
        key: Identifier for the rate limit (e.g., IP address)
        max_requests: Maximum number of requests allowed in the period
        period: Time period in seconds
        
    Returns:
        True if the request is allowed, False if rate limit exceeded
    """
    # This is a placeholder - in a real app, implement with Redis or similar
    # For now, always allow requests
    return True

def require_https(f: Callable) -> Callable:
    """
    Decorator to enforce HTTPS.
    
    Args:
        f: Function to wrap
        
    Returns:
        Wrapped function that enforces HTTPS
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_secure and not current_app.debug:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# Regular expressions for common injection patterns
SQL_INJECTION_PATTERN = re.compile(
    r'(\b(select|update|insert|delete|drop|alter|exec|union|declare|cast)\b)|(-{2})|(/\*)|(\*/)|(;)', 
    re.IGNORECASE
)

def check_sql_injection(value: str) -> bool:
    """
    Check if a string contains potential SQL injection patterns.
    
    Args:
        value: String to check
        
    Returns:
        True if a potential SQL injection is detected, False otherwise
    """
    return bool(SQL_INJECTION_PATTERN.search(value))

def validate_input(value: str, max_length: int = 255, pattern: Optional[str] = None) -> bool:
    """
    Validate user input based on criteria.
    
    Args:
        value: String to validate
        max_length: Maximum allowed length
        pattern: Optional regex pattern the input must match
        
    Returns:
        True if input is valid, False otherwise
    """
    if value is None or len(value) > max_length:
        return False
    
    # Check for potential SQL injection
    if check_sql_injection(value):
        return False
    
    # Validate against pattern if provided
    if pattern and not re.match(pattern, value):
        return False
    
    return True 