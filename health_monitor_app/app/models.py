"""
Database models for the Health Monitor application.
This module defines the database models using SQLAlchemy ORM.
"""
# Standard library imports
from datetime import datetime
from typing import Optional, Dict, Any, List, Union
import json

# Third-party imports
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.ext.declarative import declared_attr

# Application imports
from .extensions import db, login

class User(UserMixin, db.Model):
    """
    User model representing application users.
    
    Attributes:
        id: Primary key for user identification
        email: User's email address (unique)
        username: User's chosen username (unique)
        password_hash: Hashed user password
        created_at: Timestamp when the user was created
        date_of_birth: User's date of birth
        gender: User's gender
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    
    # Add relationships
    health_data = db.relationship('HealthData', backref='user', lazy='dynamic')
    
    def set_password(self, password: str) -> None:
        """
        Set user password by generating and storing a password hash.
        
        Args:
            password: The plain text password to hash and store
        """
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password: str) -> bool:
        """
        Verify a password against the stored hash.
        
        Args:
            password: The plain text password to check
            
        Returns:
            True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)
    
    def get_age(self) -> Optional[int]:
        """
        Calculate user's age based on date of birth if available.
        
        Returns:
            Age in years or None if date_of_birth not set
        """
        if hasattr(self, 'date_of_birth') and self.date_of_birth:
            today = datetime.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
        
    def initialize_settings(self) -> None:
        """
        Initialize user settings with default values if they don't exist.
        
        This creates a new UserSettings instance for the user with default values.
        """
        if not hasattr(self, 'settings') or self.settings is None:
            from .extensions import db
            settings = UserSettings(user_id=self.id)
            db.session.add(settings)
            db.session.commit()

@login.user_loader
def load_user(user_id: str) -> Optional[User]:
    """
    Load a user from the database for Flask-Login.
    
    Args:
        user_id: The ID of the user to load
        
    Returns:
        The User object or None if not found
    """
    return User.query.get(int(user_id))

class HealthData(db.Model):
    """
    Health data model for storing user health metrics.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User model
        date: Date and time when data was recorded
        weight: User's weight in kg
        blood_pressure_systolic: Systolic blood pressure in mmHg
        blood_pressure_diastolic: Diastolic blood pressure in mmHg
        heart_rate: Heart rate in beats per minute
        temperature: Body temperature in Celsius
        oxygen_saturation: Blood oxygen level in percentage
        steps: Number of steps taken
        exercise_duration: Exercise duration in minutes
        calories_burned: Calories burned during exercise
        sleep_duration: Sleep duration in hours
        sleep_quality: Sleep quality rating (1-10)
        water_intake: Water consumption in liters
        calorie_intake: Calorie consumption
        stress_level: Stress level rating (1-10)
        mood: Mood description
        notes: Additional notes
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Physical measurements
    weight = db.Column(db.Float)
    blood_pressure_systolic = db.Column(db.Integer)
    blood_pressure_diastolic = db.Column(db.Integer)
    heart_rate = db.Column(db.Integer)
    temperature = db.Column(db.Float)
    oxygen_saturation = db.Column(db.Float)
    
    # Activity data
    steps = db.Column(db.Integer)
    exercise_duration = db.Column(db.Integer)
    calories_burned = db.Column(db.Integer)
    
    # Sleep data
    sleep_duration = db.Column(db.Float)
    sleep_quality = db.Column(db.Integer)
    
    # Nutrition data
    water_intake = db.Column(db.Float)
    calorie_intake = db.Column(db.Integer)
    
    # Mental health
    stress_level = db.Column(db.Integer)
    mood = db.Column(db.String(50))
    
    # Additional info
    notes = db.Column(db.Text)

class UserSettings(db.Model):
    """
    User settings model for storing user preferences.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User model
        dark_mode: Whether dark mode is enabled
        notification_enabled: Whether notifications are enabled
        dashboard_widgets: JSON string of dashboard widget configuration
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    dark_mode = db.Column(db.Boolean, default=False)
    notification_enabled = db.Column(db.Boolean, default=True)
    dashboard_widgets = db.Column(db.String(500), default="[]")  # JSON string of widget config
    show_baselines = db.Column(db.Boolean, default=True)
    
    # Add bidirectional relationship
    user = db.relationship('User', backref=db.backref('settings', uselist=False))

class MetadataBaseline(db.Model):
    """
    Metadata baseline model for storing reference health data by demographic.
    
    Attributes:
        id: Primary key
        gender: Gender category (male, female, other)
        age_group: Age group (e.g. "18-29", "30-39")
        metric_type: Type of health metric (e.g. "weight", "heart_rate")
        avg_value: Average value for this demographic
        min_value: Minimum healthy value
        max_value: Maximum healthy value
        metadata_json: Additional metadata as JSON string
    """
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(20), nullable=False)
    age_group = db.Column(db.String(20), nullable=False)
    metric_type = db.Column(db.String(50), nullable=False)
    avg_value = db.Column(db.Float, nullable=False)
    min_value = db.Column(db.Float, nullable=False)
    max_value = db.Column(db.Float, nullable=False)
    metadata_json = db.Column(db.Text)  # JSON string with additional metadata
    
    @staticmethod
    def get_baseline(gender: str, age: int, metric_type: str) -> Optional[Dict[str, Any]]:
        """
        Get baseline data for a specific gender, age and metric.
        
        Args:
            gender: User gender
            age: User age in years
            metric_type: Type of health metric
            
        Returns:
            Dictionary with baseline data or None if not found
        """
        # Map age to age group
        age_group = None
        if age < 30:
            age_group = "18-29"
        elif age < 40:
            age_group = "30-39"
        elif age < 50:
            age_group = "40-49"
        elif age < 60:
            age_group = "50-59"
        elif age < 70:
            age_group = "60-69"
        else:
            age_group = "70+"
            
        baseline = MetadataBaseline.query.filter_by(
            gender=gender,
            age_group=age_group,
            metric_type=metric_type
        ).first()
        
        if not baseline:
            return None
            
        result = {
            "avg": baseline.avg_value,
            "min": baseline.min_value,
            "max": baseline.max_value
        }
        
        # Add metadata if available
        if baseline.metadata_json:
            try:
                metadata = json.loads(baseline.metadata_json)
                result.update(metadata)
            except json.JSONDecodeError:
                pass
                
        return result 