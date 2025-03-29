"""
Main routes for the Health Monitor application.
This module handles the main views including the dashboard and about page.
"""
from flask import render_template, flash, redirect, url_for, current_app, Response, request
from flask_login import login_required, current_user, logout_user
from typing import Dict, Any, Union, List, TYPE_CHECKING, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from sqlalchemy.exc import SQLAlchemyError

# Application imports
from ..extensions import db
from ..models import HealthData, User, UserSettings, MetadataBaseline
from . import main
from ..forms import ProfileForm, SettingsForm, DeleteAccountForm
from ..security import sanitize_input

# Type definitions for better type checking
if TYPE_CHECKING:
    from werkzeug.wrappers import Response as WerkzeugResponse
    ResponseType = Union[str, WerkzeugResponse, Response]

@main.route('/')
def index() -> ResponseType:
    """
    Display the landing page for non-authenticated users.
    If user is logged in, redirect to dashboard.
    
    Returns:
        Rendered landing template or redirect to dashboard
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/landing.html', title='Welcome to Health Monitor')

@main.route('/dashboard')
@main.route('/index')
@login_required
def dashboard() -> Union[str, Response]:
    """
    Render the dashboard home page with health data summary.
    
    Retrieves the latest health metrics and trends for display
    on the dashboard. Requires authentication.
    
    Returns:
        Rendered dashboard template with health data
    """
    try:
        # Get the latest health records for the current user
        latest_records = HealthData.query.filter_by(user_id=current_user.id)\
            .order_by(HealthData.date.desc())\
            .limit(5).all()
        
        # Get some basic statistics
        record_count = HealthData.query.filter_by(user_id=current_user.id).count()
        
        # Get record from last week for comparison
        now = datetime.utcnow()
        one_week_ago = now - timedelta(days=7)
        
        recent_stats = {
            'weight': None,
            'steps': None,
            'heart_rate': None
        }
        
        # Get recent values for key metrics
        latest_weight = HealthData.query.filter(
            HealthData.user_id == current_user.id,
            HealthData.weight.isnot(None)
        ).order_by(HealthData.date.desc()).first()
        
        latest_steps = HealthData.query.filter(
            HealthData.user_id == current_user.id,
            HealthData.steps.isnot(None)
        ).order_by(HealthData.date.desc()).first()
        
        latest_heart_rate = HealthData.query.filter(
            HealthData.user_id == current_user.id,
            HealthData.heart_rate.isnot(None)
        ).order_by(HealthData.date.desc()).first()
        
        if latest_weight:
            recent_stats['weight'] = latest_weight.weight
            
        if latest_steps:
            recent_stats['steps'] = latest_steps.steps
            
        if latest_heart_rate:
            recent_stats['heart_rate'] = latest_heart_rate.heart_rate
        
        # Initialize settings if they don't exist yet
        if not current_user.settings:
            current_user.initialize_settings()
        
        # Get baseline data if available
        baselines = {}
        if current_user.gender and current_user.date_of_birth:
            age = current_user.get_age()
            if age:
                for metric in ['weight', 'heart_rate', 'steps']:
                    baseline = MetadataBaseline.get_baseline(
                        gender=current_user.gender,
                        age=age,
                        metric_type=metric
                    )
                    if baseline:
                        baselines[metric] = baseline
        
        return render_template('main/dashboard.html', 
                              title='Dashboard',
                              latest_records=latest_records,
                              record_count=record_count,
                              recent_stats=recent_stats,
                              baselines=baselines)
    
    except Exception as e:
        current_app.logger.error(f"Error in dashboard view: {str(e)}")
        flash("Error loading dashboard. Please try again.", "danger")
        return render_template('main/dashboard.html', title='Dashboard')

def generate_dashboard_charts() -> Dict[str, str]:
    """
    Generate mini charts for the dashboard.
    
    Returns:
        Dictionary of chart names and their base64-encoded images
    """
    charts = {}
    
    # Get the last 30 days of data
    thirty_days_ago = datetime.now() - timedelta(days=30)
    all_records = HealthData.query.filter(HealthData.date >= thirty_days_ago)\
                                 .order_by(HealthData.date.asc()).all()
    
    if all_records and len(all_records) > 1:
        try:
            # Convert to DataFrame for easier manipulation
            data = [{
                'date': record.date,
                'weight': record.weight,
                'systolic': record.blood_pressure_systolic,
                'diastolic': record.blood_pressure_diastolic,
                'heart_rate': record.heart_rate,
                'steps': record.steps,
                'sleep_duration': record.sleep_duration
            } for record in all_records]

            df = pd.DataFrame(data)
            
            # Generate charts
            if 'weight' in df.columns and df['weight'].notna().any():
                charts['weight'] = create_trend_chart(df, 'weight', 'blue', 'Weight (kg)')
            
            if 'systolic' in df.columns and 'diastolic' in df.columns and \
               df['systolic'].notna().any() and df['diastolic'].notna().any():
                charts['blood_pressure'] = create_blood_pressure_chart(df)
            
            if 'heart_rate' in df.columns and df['heart_rate'].notna().any():
                charts['heart_rate'] = create_trend_chart(df, 'heart_rate', 'green', 'Heart Rate (bpm)')
            
        except Exception as e:
            current_app.logger.error(f"Error generating dashboard charts: {str(e)}")
    
    return charts

def create_trend_chart(df: pd.DataFrame, column: str, color: str, ylabel: str) -> str:
    """
    Create a line chart for a single metric.
    
    Args:
        df: DataFrame with the data
        column: Column name to plot
        color: Line color
        ylabel: Y-axis label
        
    Returns:
        Base64 encoded image
    """
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(df['date'], df[column], 'o-', color=color)
    ax.set_xlabel('Date')
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)
    fig.autofmt_xdate()
    fig.tight_layout()
    
    img = BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    chart_data = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)
    
    return chart_data

def create_blood_pressure_chart(df: pd.DataFrame) -> str:
    """
    Create a line chart for blood pressure.
    
    Args:
        df: DataFrame with systolic and diastolic data
        
    Returns:
        Base64 encoded image
    """
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(df['date'], df['systolic'], 'o-', color='red', label='Systolic')
    ax.plot(df['date'], df['diastolic'], 'o-', color='blue', label='Diastolic')
    ax.set_xlabel('Date')
    ax.set_ylabel('Blood Pressure (mmHg)')
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()
    
    img = BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    chart_data = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)
    
    return chart_data

def calculate_trend(metric_type: str, current_record: Optional[HealthData]) -> Dict[str, Any]:
    """
    Calculate the trend for a health metric compared to the previous week.
    
    Args:
        metric_type: The type of health metric (e.g., 'weight', 'blood_pressure')
        current_record: The most recent health data record
        
    Returns:
        Dictionary containing trend data including value, percentage, and direction
    """
    trend = {
        'value': 0,
        'percentage': 0,
        'direction': 'neutral'
    }
    
    if not current_record:
        return trend
    
    # Get the date from one week ago
    one_week_ago = datetime.now() - timedelta(days=7)
    
    try:
        # Get the health data record from one week ago
        previous_record = HealthData.query.filter(HealthData.date < one_week_ago).order_by(HealthData.date.desc()).first()
        
        if not previous_record:
            return trend
        
        if metric_type == 'weight':
            if current_record.weight and previous_record.weight:
                trend['value'] = round(current_record.weight - previous_record.weight, 1)
                trend['percentage'] = round((trend['value'] / previous_record.weight) * 100, 1) if previous_record.weight else 0
        
        elif metric_type == 'blood_pressure':
            if (current_record.blood_pressure_systolic and previous_record.blood_pressure_systolic and
                current_record.blood_pressure_diastolic and previous_record.blood_pressure_diastolic):
                
                # Calculate trend for systolic
                systolic_diff = current_record.blood_pressure_systolic - previous_record.blood_pressure_systolic
                systolic_perc = round((systolic_diff / previous_record.blood_pressure_systolic) * 100, 1) if previous_record.blood_pressure_systolic else 0
                
                # Calculate trend for diastolic
                diastolic_diff = current_record.blood_pressure_diastolic - previous_record.blood_pressure_diastolic
                diastolic_perc = round((diastolic_diff / previous_record.blood_pressure_diastolic) * 100, 1) if previous_record.blood_pressure_diastolic else 0
                
                # Use average of systolic and diastolic trends
                trend['value'] = round((systolic_diff + diastolic_diff) / 2, 1)
                trend['percentage'] = round((systolic_perc + diastolic_perc) / 2, 1)
        
        elif metric_type == 'heart_rate':
            if current_record.heart_rate and previous_record.heart_rate:
                trend['value'] = current_record.heart_rate - previous_record.heart_rate
                trend['percentage'] = round((trend['value'] / previous_record.heart_rate) * 100, 1) if previous_record.heart_rate else 0
        
        elif metric_type == 'oxygen_saturation':
            if current_record.oxygen_saturation and previous_record.oxygen_saturation:
                trend['value'] = round(current_record.oxygen_saturation - previous_record.oxygen_saturation, 1)
                trend['percentage'] = round((trend['value'] / previous_record.oxygen_saturation) * 100, 1) if previous_record.oxygen_saturation else 0
        
        elif metric_type == 'temperature':
            if current_record.temperature and previous_record.temperature:
                trend['value'] = round(current_record.temperature - previous_record.temperature, 1)
                trend['percentage'] = round((trend['value'] / previous_record.temperature) * 100, 1) if previous_record.temperature else 0
        
        elif metric_type == 'sleep':
            if current_record.sleep_duration and previous_record.sleep_duration:
                trend['value'] = round(current_record.sleep_duration - previous_record.sleep_duration, 1)
                trend['percentage'] = round((trend['value'] / previous_record.sleep_duration) * 100, 1) if previous_record.sleep_duration else 0
        
        # Determine direction
        if trend['value'] > 0:
            trend['direction'] = 'up'
        elif trend['value'] < 0:
            trend['direction'] = 'down'
        else:
            trend['direction'] = 'neutral'
            
    except Exception as e:
        current_app.logger.error(f"Error calculating {metric_type} trend: {str(e)}")
        trend = {'value': 0, 'percentage': 0, 'direction': 'neutral'}
    
    return trend

@main.route('/about')
def about() -> str:
    """
    Render the about page of the application.
    
    Returns:
        Rendered about template
    """
    return render_template('main/about.html', title='About Health Monitor')

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile() -> Union[str, Response]:
    """
    Display and update user profile information.
    
    Returns:
        Rendered profile template or redirect
    """
    form = ProfileForm()
    
    if form.validate_on_submit():
        try:
            # Update user profile with form data
            current_user.first_name = sanitize_input(form.first_name.data)
            current_user.last_name = sanitize_input(form.last_name.data)
            current_user.gender = form.gender.data
            current_user.date_of_birth = form.date_of_birth.data
            current_user.height = form.height.data
            current_user.weight = form.weight.data
            
            db.session.commit()
            
            current_app.logger.info(f"User {current_user.username} updated their profile")
            flash('Your profile has been updated successfully.', 'success')
            return redirect(url_for('main.profile'))
            
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error updating profile: {str(e)}")
            flash('A database error occurred. Your profile could not be updated.', 'danger')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected error in profile update: {str(e)}")
            flash('An unexpected error occurred. Please try again.', 'danger')
    
    elif request.method == 'GET':
        # Pre-populate form with user data
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.gender.data = current_user.gender
        form.date_of_birth.data = current_user.date_of_birth
        form.height.data = current_user.height
        form.weight.data = current_user.weight
    
    return render_template('main/profile.html', 
                          title='Your Profile',
                          form=form)

@main.route('/settings', methods=['GET', 'POST'])
@login_required
def settings() -> Union[str, Response]:
    """
    Display and update user settings.
    
    Returns:
        Rendered settings template or redirect
    """
    # Ensure user has settings initialized
    if not current_user.settings:
        current_user.initialize_settings()
        db.session.commit()
    
    form = SettingsForm()
    
    if form.validate_on_submit():
        try:
            # Update settings with form data
            settings = current_user.settings
            settings.weight_unit = form.weight_unit.data
            settings.height_unit = form.height_unit.data
            settings.temperature_unit = form.temperature_unit.data
            settings.distance_unit = form.distance_unit.data
            settings.volume_unit = form.volume_unit.data
            settings.theme = form.theme.data
            settings.notifications_enabled = form.notifications_enabled.data
            
            db.session.commit()
            
            current_app.logger.info(f"User {current_user.username} updated their settings")
            flash('Your settings have been updated successfully.', 'success')
            return redirect(url_for('main.settings'))
            
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error updating settings: {str(e)}")
            flash('A database error occurred. Your settings could not be updated.', 'danger')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected error in settings update: {str(e)}")
            flash('An unexpected error occurred. Please try again.', 'danger')
    
    elif request.method == 'GET':
        # Pre-populate form with current settings
        settings = current_user.settings
        form.weight_unit.data = settings.weight_unit
        form.height_unit.data = settings.height_unit
        form.temperature_unit.data = settings.temperature_unit
        form.distance_unit.data = settings.distance_unit
        form.volume_unit.data = settings.volume_unit
        form.theme.data = settings.theme
        form.notifications_enabled.data = settings.notifications_enabled
    
    # Get unit options for the template
    unit_options = UserSettings.get_unit_options()
    
    return render_template('main/settings.html', 
                          title='Your Settings',
                          form=form,
                          unit_options=unit_options)

@main.route('/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account() -> Union[str, Response]:
    """
    Handle account deletion with confirmation.
    
    Returns:
        Rendered template or redirect
    """
    form = DeleteAccountForm()
    
    if form.validate_on_submit():
        try:
            # Additional security: verify password again
            if not current_user.check_password(form.password.data):
                flash('Incorrect password. Account deletion cancelled.', 'danger')
                return redirect(url_for('main.delete_account'))
            
            # Get username for logging
            username = current_user.username
            
            # Delete the user account (this will cascade to all related records)
            current_user.delete_account()
            
            # Log the account deletion
            current_app.logger.info(f"User account deleted: {username}")
            
            # Log out the user
            logout_user()
            
            flash('Your account has been permanently deleted.', 'success')
            return redirect(url_for('main.index'))
            
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error during account deletion: {str(e)}")
            flash('A database error occurred. Your account could not be deleted.', 'danger')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected error in account deletion: {str(e)}")
            flash('An unexpected error occurred. Please try again.', 'danger')
    
    return render_template('main/delete_account.html', 
                          title='Delete Your Account',
                          form=form) 