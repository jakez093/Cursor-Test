"""
Common form validation and security for Health Monitor application.

This module provides common form validation and security features that can be
used across different forms in the application.
"""
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import validators
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, Optional, 
    NumberRange, ValidationError, Regexp
)
from wtforms import (
    StringField, PasswordField, BooleanField, SelectField,
    DateField, FloatField, TextAreaField, SubmitField,
    RadioField, DecimalField
)
from wtforms.fields.simple import TextAreaField
import re
from datetime import date, timedelta
from .models import User

# Common password validation
def validate_password_strength(form, field):
    """
    Validate password strength.
    
    Requirements:
    - At least 8 characters
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one number
    - Contains at least one special character
    """
    password = field.data
    
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long.')
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain at least one uppercase letter.')
    
    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must contain at least one lowercase letter.')
    
    if not re.search(r'[0-9]', password):
        raise ValidationError('Password must contain at least one number.')
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError('Password must contain at least one special character.')

def validate_no_whitespace(form, field):
    """Validate that field does not contain whitespace."""
    if field.data and ' ' in field.data:
        raise ValidationError('This field cannot contain spaces.')

def validate_birth_date(form, field):
    """Validate that the birth date is reasonable."""
    if field.data:
        today = date.today()
        age = today.year - field.data.year - ((today.month, today.day) < (field.data.month, field.data.day))
        
        if age < 13:
            raise ValidationError('You must be at least 13 years old to use this application.')
        
        if age > 120:
            raise ValidationError('Please enter a valid birth date.')

# Username validation regex - only letters, numbers, dots and underscores
username_regexp = re.compile(r'^[\w.]+$')

# Define security-related fields that can be reused across forms
class SecurityMixin:
    """Mixin to add security-related fields to forms."""
    
    # Anti-CSRF token is automatically added by Flask-WTF's FlaskForm
    
    # Can be enabled for high-security forms in production
    # recaptcha = RecaptchaField()
    
    # User agreement checkbox for registrations/sensitive actions
    accept_terms = BooleanField('I agree to the Terms of Service and Privacy Policy', 
                              validators=[DataRequired()])

# Common username field with validation
class UsernameField(StringField):
    """Username field with standard validation."""
    
    def __init__(self, label='Username', validators=None, **kwargs):
        if validators is None:
            validators = []
        
        validators.extend([
            DataRequired(),
            Length(min=3, max=64),
            Regexp(username_regexp, message="Username can only contain letters, numbers, dots, and underscores.")
        ])
        
        super().__init__(label, validators, **kwargs)

# Common email field with validation
class EmailField(StringField):
    """Email field with standard validation."""
    
    def __init__(self, label='Email', validators=None, **kwargs):
        if validators is None:
            validators = []
        
        validators.extend([
            DataRequired(),
            Email(),
            Length(max=120)
        ])
        
        super().__init__(label, validators, **kwargs)

# Common password field with validation
class PasswordField(PasswordField):
    """Password field with standard validation."""
    
    def __init__(self, label='Password', validators=None, **kwargs):
        if validators is None:
            validators = []
        
        validators.extend([
            DataRequired(),
            validate_password_strength
        ])
        
        super().__init__(label, validators, **kwargs)

class ProfileForm(FlaskForm):
    """Form for updating user profile information."""
    first_name = StringField('First Name', validators=[Length(max=50)])
    last_name = StringField('Last Name', validators=[Length(max=50)])
    gender = SelectField('Gender', choices=[
        ('', 'Select Gender'),
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say')
    ])
    date_of_birth = DateField('Date of Birth', validators=[Optional(), validate_birth_date], format='%Y-%m-%d')
    height = FloatField('Height (cm)', validators=[Optional(), NumberRange(min=50, max=250)])
    weight = FloatField('Weight (kg)', validators=[Optional(), NumberRange(min=20, max=300)])
    
    # Password confirmation to authorize changes
    current_password = PasswordField('Enter your current password to confirm changes', 
                                    validators=[DataRequired()])
    
    submit = SubmitField('Update Profile')
    
    def validate_current_password(self, field):
        """Validate that the current password is correct."""
        from flask_login import current_user
        if not current_user.check_password(field.data):
            raise ValidationError('Incorrect password. Please try again.')

class SettingsForm(FlaskForm):
    """Form for updating user settings."""
    # Units of measurement
    weight_unit = SelectField('Weight Unit', choices=[
        ('kg', 'Kilograms (kg)'),
        ('lb', 'Pounds (lb)')
    ])
    height_unit = SelectField('Height Unit', choices=[
        ('cm', 'Centimeters (cm)'),
        ('in', 'Inches (in)')
    ])
    temperature_unit = SelectField('Temperature Unit', choices=[
        ('celsius', 'Celsius (°C)'),
        ('fahrenheit', 'Fahrenheit (°F)')
    ])
    distance_unit = SelectField('Distance Unit', choices=[
        ('km', 'Kilometers (km)'),
        ('mi', 'Miles (mi)')
    ])
    volume_unit = SelectField('Volume Unit', choices=[
        ('l', 'Liters (L)'),
        ('oz', 'Fluid Ounces (fl oz)')
    ])
    
    # Display preferences
    theme = SelectField('Theme', choices=[
        ('light', 'Light Theme'),
        ('dark', 'Dark Theme'),
        ('system', 'System Default')
    ])
    show_baselines = BooleanField('Comparison Baselines')
    dark_mode = BooleanField('Dark Mode')
    graph_time_period = SelectField('Default Graph Time Period', choices=[
        ('7d', 'Last 7 Days'),
        ('1m', 'Last Month'),
        ('3m', 'Last 3 Months'),
        ('all', 'All Time')
    ])
    notifications_enabled = BooleanField('Enable Notifications')
    
    submit = SubmitField('Save Settings')

class DeleteAccountForm(FlaskForm, SecurityMixin):
    """Form for confirming account deletion."""
    confirm_text = StringField(
        'Type "DELETE" to confirm', 
        validators=[
            DataRequired(),
            Regexp(r'^DELETE$', message='Please type DELETE (all caps) to confirm account deletion.')
        ]
    )
    password = PasswordField('Enter your password', validators=[DataRequired()])
    
    # Include terms agreement from SecurityMixin
    
    submit = SubmitField('Delete My Account Permanently')
    
    def validate_password(self, field):
        """Validate that the password is correct."""
        from flask_login import current_user
        if not current_user.check_password(field.data):
            raise ValidationError('Incorrect password. Please try again.') 