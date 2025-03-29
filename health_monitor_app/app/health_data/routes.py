"""
Health data routes for the Health Monitor application.

This module defines the routes for health data operations, including
adding, viewing, updating, and deleting health records.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, Response, abort
from flask_login import login_required, current_user
from ..extensions import db
from ..models import HealthData, User
from . import health_data
from .forms import HealthDataForm
from datetime import datetime, timedelta, date
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from typing import Dict, List, Optional, Tuple, Union, Any, cast, TypeVar, TYPE_CHECKING
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Query
from ..security import sanitize_input, sanitize_form_data, validate_input
import re

# Type definitions for better type checking
if TYPE_CHECKING:
    from flask import Flask
    from werkzeug.wrappers import Response as WerkzeugResponse
    ResponseType = Union[str, WerkzeugResponse, Response]

# Define unit mapping for each parameter (constant)
UNIT_MAPPING = {
    'weight': 'kg',
    'systolic': 'mmHg',
    'diastolic': 'mmHg',
    'blood_pressure': 'mmHg',
    'heart_rate': 'bpm',
    'steps': 'steps',
    'sleep_duration': 'hours',
    'water_intake': 'liters',
    'calorie_intake': 'kcal',
    'stress_level': '/10'
}

# Valid parameters for graphs and visualization
VALID_PARAMETERS = [
    'weight', 'blood_pressure', 'heart_rate', 'steps', 
    'sleep_duration', 'water_intake', 'calorie_intake', 'stress_level'
]

# Valid time periods for filtering
VALID_TIME_PERIODS = ['week', 'month', 'quarter']

# Error message constant
ERROR_GENERIC = 'An unexpected error occurred. Please try again.'

# Create blueprint
health_data = Blueprint('health_data', __name__)

@health_data.route('/dashboard')
@login_required
def dashboard():
    """
    Display the user dashboard with health data summary.
    
    Shows recent health metrics and provides navigation to detailed views.
    """
    # Get user's most recent health data entry
    recent_data = HealthData.query.filter_by(user_id=current_user.id).order_by(
        HealthData.date.desc()).first()
        
    return render_template('health_data/dashboard.html', 
                           title='Dashboard',
                           recent_data=recent_data)

@health_data.route('/add', methods=['GET', 'POST'])
@login_required
def add_health_data():
    """
    Add new health data for the current user.
    
    GET: Display form for adding health data
    POST: Process form submission and add data
    """
    form = HealthDataForm()
    if form.validate_on_submit():
        try:
            # Create new health data record
            health_data = HealthData(
                user_id=current_user.id,
                weight=form.weight.data,
                blood_pressure_systolic=form.blood_pressure_systolic.data,
                blood_pressure_diastolic=form.blood_pressure_diastolic.data,
                heart_rate=form.heart_rate.data,
                temperature=form.temperature.data,
                oxygen_saturation=form.oxygen_saturation.data,
                steps=form.steps.data,
                exercise_duration=form.exercise_duration.data,
                calories_burned=form.calories_burned.data,
                sleep_duration=form.sleep_duration.data,
                sleep_quality=form.sleep_quality.data,
                water_intake=form.water_intake.data,
                calorie_intake=form.calorie_intake.data,
                stress_level=form.stress_level.data,
                mood=form.mood.data,
                notes=form.notes.data
            )
            db.session.add(health_data)
            db.session.commit()
            
            flash('Health data added successfully!', 'success')
            return redirect(url_for('health_data.view_all_data'))
        except Exception:
            db.session.rollback()
            flash(ERROR_GENERIC, 'error')
    
    return render_template('health_data/add_data.html', 
                           title='Add Health Data', 
                           form=form)

@health_data.route('/history')
@login_required
def history() -> str:
    """
    Display the user's health data history with pagination.

    Also generates mini preview charts for quick visualization of trends.

    Returns:
        Rendered template with health records and preview charts
    """
    try:
        # Validate and sanitize page input
        try:
            page = request.args.get('page', 1, type=int)
            if page < 1:
                page = 1
        except (ValueError, TypeError):
            page = 1
        
        # Query user's health records with pagination
        health_records = HealthData.query.filter_by(user_id=current_user.id)\
            .order_by(HealthData.date.desc())\
            .paginate(page=page, per_page=10, error_out=False)
        
        # Generate mini preview charts
        preview_charts: Dict[str, str] = {}
        
        # Get all data for charts
        all_records = HealthData.query.filter_by(user_id=current_user.id)\
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

                # Create mini charts
                for param, color in [
                    ('weight', 'blue'),
                    ('heart_rate', 'green'),
                    ('steps', 'orange'),
                    ('sleep_duration', 'purple')
                ]:
                    if param in df.columns and df[param].notna().any():
                        preview_charts[param] = create_mini_chart(df, param, color)

            except Exception as e:
                current_app.logger.error(f"Error generating preview charts: {str(e)}")
                flash("Error generating preview charts. Some visualizations may not be available.", "warning")

        return render_template('health_data/history.html', title='Health Data History',
                              health_records=health_records, preview_charts=preview_charts)

    except Exception as e:
        current_app.logger.error(f"Error in history view: {str(e)}")
        flash("Error loading health history. Please try again.", "danger")
        return render_template('health_data/history.html', title='Health Data History',
                              health_records=None, preview_charts={})

def create_mini_chart(df: pd.DataFrame, parameter: str, color: str) -> str:
    """
    Create a mini chart for the specified parameter.

    Args:
        df: DataFrame containing the data
        parameter: Parameter to plot
        color: Color for the line

    Returns:
        Base64 encoded image string
    """
    # Security check: validate parameter
    if parameter not in df.columns:
        current_app.logger.warning(f"Invalid parameter requested for chart: {parameter}")
        return ""
        
    fig, ax = plt.subplots(figsize=(3, 1.5))
    ax.plot(df['date'], df[parameter], '-', color=color)
    ax.set_title(parameter.replace('_', ' ').title(), fontsize=8)
    ax.tick_params(axis='both', which='both', labelsize=6)
    fig.tight_layout()

    img = BytesIO()
    fig.savefig(img, format='png', dpi=80)
    img.seek(0)
    chart = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)
    return chart

@health_data.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_health_data(id: int) -> Union[str, Response]:
    """
    Edit an existing health data record.

    Args:
        id: The ID of the health data record to edit

    Returns:
        Rendered template or redirect
    """
    try:
        # Validate id parameter
        if not isinstance(id, int) or id <= 0:
            current_app.logger.warning(f"Invalid health data ID requested: {id}")
            flash('Invalid health data record.', 'danger')
            return redirect(url_for('health_data.history'))
            
        data = HealthData.query.get_or_404(id)

        # Security check: ensure the health data belongs to the current user
        if data.user_id != current_user.id:
            current_app.logger.warning(
                f"User {current_user.username} attempted to edit health data belonging to user ID {data.user_id}"
            )
            flash('You do not have permission to edit this data.', 'danger')
            return redirect(url_for('health_data.history'))

        form = HealthDataForm()
        if form.validate_on_submit():
            # Sanitize text inputs
            sanitized_notes = sanitize_input(form.notes.data) if form.notes.data else None
            sanitized_mood = sanitize_input(form.mood.data) if form.mood.data else None
            
            data.weight = form.weight.data
            data.blood_pressure_systolic = form.blood_pressure_systolic.data
            data.blood_pressure_diastolic = form.blood_pressure_diastolic.data
            data.heart_rate = form.heart_rate.data
            data.temperature = form.temperature.data
            data.oxygen_saturation = form.oxygen_saturation.data
            data.steps = form.steps.data
            data.exercise_duration = form.exercise_duration.data
            data.calories_burned = form.calories_burned.data
            data.sleep_duration = form.sleep_duration.data
            data.sleep_quality = form.sleep_quality.data
            data.water_intake = form.water_intake.data
            data.calorie_intake = form.calorie_intake.data
            data.stress_level = form.stress_level.data
            data.mood = sanitized_mood
            data.notes = sanitized_notes

            try:
                db.session.commit()
                current_app.logger.info(f"Health data record {id} updated by user {current_user.username}")
                flash('Health data updated successfully!', 'success')
                return redirect(url_for('health_data.history'))
            except SQLAlchemyError as e:
                db.session.rollback()
                current_app.logger.error(f"Database error when updating health data: {str(e)}")
                flash('Database error when updating health data. Please try again.', 'danger')
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Unexpected error when updating health data: {str(e)}")
                flash(ERROR_GENERIC, 'danger')

        elif request.method == 'GET':
            # Populate form with existing data
            form.weight.data = data.weight
            form.blood_pressure_systolic.data = data.blood_pressure_systolic
            form.blood_pressure_diastolic.data = data.blood_pressure_diastolic
            form.heart_rate.data = data.heart_rate
            form.temperature.data = data.temperature
            form.oxygen_saturation.data = data.oxygen_saturation
            form.steps.data = data.steps
            form.exercise_duration.data = data.exercise_duration
            form.calories_burned.data = data.calories_burned
            form.sleep_duration.data = data.sleep_duration
            form.sleep_quality.data = data.sleep_quality
            form.water_intake.data = data.water_intake
            form.calorie_intake.data = data.calorie_intake
            form.stress_level.data = data.stress_level
            form.mood.data = data.mood
            form.notes.data = data.notes

        return render_template('health_data/edit.html', title='Edit Health Data', form=form)

    except SQLAlchemyError as e:
        current_app.logger.error(f"Database error when retrieving health data for editing: {str(e)}")
        flash('Error loading health data. Please try again.', 'danger')
        return redirect(url_for('health_data.history'))
    except Exception as e:
        current_app.logger.error(f"Unexpected error in edit health data view: {str(e)}")
        flash(ERROR_GENERIC, 'danger')
        return redirect(url_for('health_data.history'))

@health_data.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_health_data(id: int) -> Response:
    """
    Delete a health data record.

    Args:
        id: The ID of the health data record to delete

    Returns:
        Redirect to history page
    """
    try:
        # Validate id parameter
        if not isinstance(id, int) or id <= 0:
            current_app.logger.warning(f"Invalid health data ID requested for deletion: {id}")
            flash('Invalid health data record.', 'danger')
            return redirect(url_for('health_data.history'))
            
        data = HealthData.query.get_or_404(id)

        # Security check: ensure the health data belongs to the current user
        if data.user_id != current_user.id:
            current_app.logger.warning(
                f"User {current_user.username} attempted to delete health data belonging to user ID {data.user_id}"
            )
            flash('You do not have permission to delete this data.', 'danger')
            return redirect(url_for('health_data.history'))

        try:
            # Keep a reference for logging
            record_date = data.date
            
            db.session.delete(data)
            db.session.commit()
            
            current_app.logger.info(
                f"Health data record {id} from {record_date} deleted by user {current_user.username}"
            )
            flash('Health data deleted successfully!', 'success')
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error when deleting health data: {str(e)}")
            flash('Database error when deleting health data. Please try again.', 'danger')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Unexpected error when deleting health data: {str(e)}")
            flash(ERROR_GENERIC, 'danger')

        return redirect(url_for('health_data.history'))

    except SQLAlchemyError as e:
        current_app.logger.error(f"Database error when retrieving health data for deletion: {str(e)}")
        flash('Error processing request. Please try again.', 'danger')
        return redirect(url_for('health_data.history'))
    except Exception as e:
        current_app.logger.error(f"Unexpected error in delete health data view: {str(e)}")
        flash(ERROR_GENERIC, 'danger')
        return redirect(url_for('health_data.history'))

@health_data.route('/graph/<parameter>')
@health_data.route('/graph/<parameter>/<time_period>')
@health_data.route('/graph/<parameter>/<time_period>/<reference_date>')
@login_required
def view_graph(parameter: str, time_period: str = 'month', reference_date: Optional[str] = None) -> Union[str, Response]:
    """
    Display a graph for a specific health parameter.

    Args:
        parameter: Health parameter to display ('weight', 'blood_pressure', etc.)
        time_period: Time period to display ('week', 'month', 'quarter')
        reference_date: ISO format date (YYYY-MM-DD) as reference point

    Returns:
        Rendered template with graph and statistics
    """
    try:
        # Security check: validate parameter
        parameter = sanitize_input(parameter)
        if parameter not in VALID_PARAMETERS:
            current_app.logger.warning(f"Invalid parameter requested: {parameter}")
            flash('Invalid health parameter requested.', 'danger')
            return redirect(url_for('health_data.history'))
        
        # Security check: validate time_period
        time_period = sanitize_input(time_period)
        if time_period not in VALID_TIME_PERIODS:
            current_app.logger.warning(f"Invalid time period requested: {time_period}")
            time_period = 'month'  # Default to month if invalid
        
        # Validate reference_date format if provided
        if reference_date:
            reference_date = sanitize_input(reference_date)
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', reference_date):
                current_app.logger.warning(f"Invalid reference date format: {reference_date}")
                reference_date = None  # Use current date if invalid
        
        # Get all health data for the current user
        health_records = HealthData.query.filter_by(user_id=current_user.id)\
            .order_by(HealthData.date.asc()).all()

        if not health_records:
            flash('No health data available for graphing.', 'info')
            return redirect(url_for('health_data.history'))

        # Parse reference date if provided, otherwise use current date
        try:
            ref_date = (datetime.strptime(reference_date, '%Y-%m-%d').date()
                       if reference_date else date.today())
        except ValueError:
            flash('Invalid date format. Using current date.', 'warning')
            ref_date = date.today()

        # Calculate date ranges based on time period
        period_config: Dict[str, Dict[str, Union[int, str]]] = {
            'week': {'days': 7, 'label': '1 Week'},
            'quarter': {'days': 90, 'label': '3 Months'},
            'month': {'days': 30, 'label': '1 Month'}  # Default
        }

        # Get configuration for the selected time period (or default to month)
        period_info = period_config.get(time_period, period_config['month'])
        period_days = int(period_info['days'])

        # Calculate start and end dates for the selected period
        start_date = datetime.combine(ref_date - timedelta(days=period_days-1), datetime.min.time())
        end_date = datetime.combine(ref_date, datetime.max.time())

        # Calculate navigation dates
        next_date = (ref_date + timedelta(days=period_days)).strftime('%Y-%m-%d')
        prev_date = (ref_date - timedelta(days=period_days)).strftime('%Y-%m-%d')

        # Format the period text for display
        period_text = f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"

        # Convert to DataFrame for easier manipulation
        data = [{
            'date': record.date,
            'weight': record.weight,
            'systolic': record.blood_pressure_systolic,
            'diastolic': record.blood_pressure_diastolic,
            'heart_rate': record.heart_rate,
            'steps': record.steps,
            'sleep_duration': record.sleep_duration,
            'water_intake': record.water_intake,
            'calorie_intake': record.calorie_intake,
            'stress_level': record.stress_level
        } for record in health_records]

        df = pd.DataFrame(data)

        # Filter data based on time period and reference date
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

        # Check if filtered data exists
        no_data_in_period = len(df) == 0
        graph = None
        title = f"{parameter.replace('_', ' ').title()} History"
        stats: Dict[str, Dict[str, Any]] = {
            'averages': {},
            'minimums': {},
            'maximums': {},
            'latest': {},
            'trends': {}
        }

        if not no_data_in_period:
            try:
                # Generate graph based on parameter
                graph, title, stats = generate_graph(df, parameter, period_text)
            except ValueError as ve:
                current_app.logger.warning(f"Error generating graph: {str(ve)}")
                flash(f'Error generating graph: {str(ve)}', 'warning')
            except Exception as e:
                current_app.logger.error(f"Unexpected error generating graph: {str(e)}")
                flash(ERROR_GENERIC, 'danger')
                return redirect(url_for('health_data.history'))
        else:
            flash("No data available for the selected time period.", 'info')

        return render_template('health_data/graph.html',
                              title=title,
                              graph=graph,
                              parameter=parameter,
                              time_period=time_period,
                              reference_date=ref_date.strftime('%Y-%m-%d'),
                              next_date=next_date,
                              prev_date=prev_date,
                              period_text=period_text,
                              no_data_in_period=no_data_in_period,
                              averages=stats['averages'],
                              minimums=stats['minimums'],
                              maximums=stats['maximums'],
                              latest=stats['latest'],
                              units=UNIT_MAPPING,
                              trends=stats['trends'])

    except SQLAlchemyError as e:
        current_app.logger.error(f"Database error in view_graph: {str(e)}")
        flash('Error retrieving health data. Please try again.', 'danger')
        return redirect(url_for('health_data.history'))
    except Exception as e:
        current_app.logger.error(f"Unexpected error in view_graph: {str(e)}")
        flash(ERROR_GENERIC, 'danger')
        return redirect(url_for('health_data.history'))

def generate_graph(df: pd.DataFrame, parameter: str, period_text: str) -> Tuple[str, str, Dict[str, Dict[str, Any]]]:
    """
    Generate a graph for the specified health parameter.

    Args:
        df: Pandas DataFrame containing filtered health data
        parameter: Health parameter to visualize
        period_text: Text describing the time period for the graph title

    Returns:
        Tuple containing:
        - encoded_image: Base64 encoded image string
        - title: Graph title
        - statistics_dict: Dictionary of calculated statistics

    Raises:
        ValueError: If parameter is invalid or no data is available
    """
    # Initialize statistics dictionaries
    stats: Dict[str, Dict[str, Any]] = {
        'averages': {},
        'minimums': {},
        'maximums': {},
        'latest': {},
        'trends': {}
    }

    if df.empty:
        raise ValueError(f"No data available for {parameter}")

    fig, ax = plt.subplots(figsize=(10, 6))
    title = f'{parameter.replace("_", " ").title()} History - {period_text}'

    if parameter == 'weight' and 'weight' in df and df['weight'].notna().any():
        ax.plot(df['date'], df['weight'], 'o-', color='blue')
        ax.set_title(title)
        ax.set_xlabel('Date')
        ax.set_ylabel('Weight (kg)')

        # Calculate statistics
        stats['averages']['weight'] = round(float(df['weight'].mean()), 1)
        stats['minimums']['weight'] = round(float(df['weight'].min()), 1)
        stats['maximums']['weight'] = round(float(df['weight'].max()), 1)
        stats['latest']['weight'] = round(float(df['weight'].iloc[-1]), 1) if not df.empty else 'N/A'

        # Determine trend
        stats['trends']['weight'] = calculate_trend(df['weight'], threshold=0.1)

    elif parameter == 'blood_pressure' and 'systolic' in df and 'diastolic' in df and df['systolic'].notna().any() and df['diastolic'].notna().any():
        ax.plot(df['date'], df['systolic'], 'o-', color='red', label='Systolic')
        ax.plot(df['date'], df['diastolic'], 'o-', color='blue', label='Diastolic')
        ax.set_title(title)
        ax.set_xlabel('Date')
        ax.set_ylabel('Blood Pressure (mmHg)')
        ax.legend()

        # Calculate statistics for both systolic and diastolic
        if not df.empty:
            stats['averages']['blood_pressure'] = f"{round(float(df['systolic'].mean()))}/{round(float(df['diastolic'].mean()))}"
            stats['minimums']['blood_pressure'] = f"{round(float(df['systolic'].min()))}/{round(float(df['diastolic'].min()))}"
            stats['maximums']['blood_pressure'] = f"{round(float(df['systolic'].max()))}/{round(float(df['diastolic'].max()))}"
            stats['latest']['blood_pressure'] = f"{round(float(df['systolic'].iloc[-1]))}/{round(float(df['diastolic'].iloc[-1]))}"
        else:
            stats['averages']['blood_pressure'] = stats['minimums']['blood_pressure'] = stats['maximums']['blood_pressure'] = stats['latest']['blood_pressure'] = 'N/A'

        # Determine trend based on systolic
        stats['trends']['blood_pressure'] = calculate_trend(df['systolic'], threshold=1)

    elif parameter == 'heart_rate' and 'heart_rate' in df and df['heart_rate'].notna().any():
        ax.plot(df['date'], df['heart_rate'], 'o-', color='green')
        ax.set_title(title)
        ax.set_xlabel('Date')
        ax.set_ylabel('Heart Rate (bpm)')

        # Calculate statistics
        if not df.empty:
            stats['averages']['heart_rate'] = round(float(df['heart_rate'].mean()))
            stats['minimums']['heart_rate'] = int(df['heart_rate'].min())
            stats['maximums']['heart_rate'] = int(df['heart_rate'].max())
            stats['latest']['heart_rate'] = int(df['heart_rate'].iloc[-1])
        else:
            stats['averages']['heart_rate'] = stats['minimums']['heart_rate'] = stats['maximums']['heart_rate'] = stats['latest']['heart_rate'] = 'N/A'

        # Determine trend
        stats['trends']['heart_rate'] = calculate_trend(df['heart_rate'], threshold=1)

    elif parameter == 'steps' and 'steps' in df and df['steps'].notna().any():
        ax.bar(df['date'], df['steps'], color='orange')
        ax.set_title(title)
        ax.set_xlabel('Date')
        ax.set_ylabel('Steps')

        # Calculate statistics
        if not df.empty:
            stats['averages']['steps'] = round(float(df['steps'].mean()))
            stats['minimums']['steps'] = int(df['steps'].min())
            stats['maximums']['steps'] = int(df['steps'].max())
            stats['latest']['steps'] = int(df['steps'].iloc[-1])
        else:
            stats['averages']['steps'] = stats['minimums']['steps'] = stats['maximums']['steps'] = stats['latest']['steps'] = 'N/A'

        # Determine trend
        stats['trends']['steps'] = calculate_trend(df['steps'], threshold=100)

    elif parameter == 'sleep_duration' and 'sleep_duration' in df and df['sleep_duration'].notna().any():
        ax.plot(df['date'], df['sleep_duration'], 'o-', color='purple')
        ax.set_title(title)
        ax.set_xlabel('Date')
        ax.set_ylabel('Sleep Duration (hours)')

        # Calculate statistics
        if not df.empty:
            stats['averages']['sleep_duration'] = round(float(df['sleep_duration'].mean()), 1)
            stats['minimums']['sleep_duration'] = round(float(df['sleep_duration'].min()), 1)
            stats['maximums']['sleep_duration'] = round(float(df['sleep_duration'].max()), 1)
            stats['latest']['sleep_duration'] = round(float(df['sleep_duration'].iloc[-1]), 1)
        else:
            stats['averages']['sleep_duration'] = stats['minimums']['sleep_duration'] = stats['maximums']['sleep_duration'] = stats['latest']['sleep_duration'] = 'N/A'

        # Determine trend
        stats['trends']['sleep_duration'] = calculate_trend(df['sleep_duration'], threshold=0.2)

    elif parameter == 'water_intake' and 'water_intake' in df and df['water_intake'].notna().any():
        ax.bar(df['date'], df['water_intake'], color='skyblue')
        ax.set_title(title)
        ax.set_xlabel('Date')
        ax.set_ylabel('Water Intake (liters)')

        # Calculate statistics
        if not df.empty:
            stats['averages']['water_intake'] = round(float(df['water_intake'].mean()), 1)
            stats['minimums']['water_intake'] = round(float(df['water_intake'].min()), 1)
            stats['maximums']['water_intake'] = round(float(df['water_intake'].max()), 1)
            stats['latest']['water_intake'] = round(float(df['water_intake'].iloc[-1]), 1)
        else:
            stats['averages']['water_intake'] = stats['minimums']['water_intake'] = stats['maximums']['water_intake'] = stats['latest']['water_intake'] = 'N/A'

        # Determine trend
        stats['trends']['water_intake'] = calculate_trend(df['water_intake'], threshold=0.1)

    elif parameter == 'calorie_intake' and 'calorie_intake' in df and df['calorie_intake'].notna().any():
        ax.bar(df['date'], df['calorie_intake'], color='brown')
        ax.set_title(title)
        ax.set_xlabel('Date')
        ax.set_ylabel('Calories')

        # Calculate statistics
        if not df.empty:
            stats['averages']['calorie_intake'] = round(float(df['calorie_intake'].mean()))
            stats['minimums']['calorie_intake'] = int(df['calorie_intake'].min())
            stats['maximums']['calorie_intake'] = int(df['calorie_intake'].max())
            stats['latest']['calorie_intake'] = int(df['calorie_intake'].iloc[-1])
        else:
            stats['averages']['calorie_intake'] = stats['minimums']['calorie_intake'] = stats['maximums']['calorie_intake'] = stats['latest']['calorie_intake'] = 'N/A'

        # Determine trend
        stats['trends']['calorie_intake'] = calculate_trend(df['calorie_intake'], threshold=50)

    elif parameter == 'stress_level' and 'stress_level' in df and df['stress_level'].notna().any():
        ax.plot(df['date'], df['stress_level'], 'o-', color='red')
        ax.set_title(title)
        ax.set_xlabel('Date')
        ax.set_ylabel('Stress Level (1-10)')

        # Calculate statistics
        if not df.empty:
            stats['averages']['stress_level'] = round(float(df['stress_level'].mean()), 1)
            stats['minimums']['stress_level'] = int(df['stress_level'].min())
            stats['maximums']['stress_level'] = int(df['stress_level'].max())
            stats['latest']['stress_level'] = int(df['stress_level'].iloc[-1])
        else:
            stats['averages']['stress_level'] = stats['minimums']['stress_level'] = stats['maximums']['stress_level'] = stats['latest']['stress_level'] = 'N/A'

        # Determine trend
        stats['trends']['stress_level'] = calculate_trend(df['stress_level'], threshold=0.5)

    else:
        raise ValueError(f'No data available for {parameter} or parameter is invalid.')

    # Format the graph
    fig.autofmt_xdate()  # Rotate date labels
    fig.tight_layout()

    # Save to bytesIO
    img = BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    encoded_img = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)

    return encoded_img, title, stats

def calculate_trend(series: pd.Series, threshold: float = 0.1, num_points: int = 3) -> str:
    """
    Calculate the trend of a time series.

    Args:
        series: Pandas Series containing the data
        threshold: Threshold to determine if trend is significant
        num_points: Number of most recent points to consider

    Returns:
        'up', 'down', or 'neutral' depending on trend direction
    """
    if len(series) >= num_points:
        recent_data = series.tail(num_points)
        try:
            # Convert data indices to numeric range for fitting
            x_range = np.arange(len(recent_data))
            # Convert series values to float for calculation
            y_values = recent_data.astype(float).values
            # Calculate trend slope
            slope = np.polyfit(x_range, y_values, 1)[0]

            if slope > threshold:
                return 'up'
            elif slope < -threshold:
                return 'down'
        except (ValueError, TypeError) as e:
            current_app.logger.warning(f"Error calculating trend: {str(e)}")
            return 'neutral'

    return 'neutral'