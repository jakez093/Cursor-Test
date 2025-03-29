from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange

class HealthDataForm(FlaskForm):
    # Vital signs
    weight = FloatField('Weight (kg)', validators=[Optional(), NumberRange(min=0, max=500)])
    blood_pressure_systolic = IntegerField('Systolic Blood Pressure (mmHg)', 
                                          validators=[Optional(), NumberRange(min=60, max=250)])
    blood_pressure_diastolic = IntegerField('Diastolic Blood Pressure (mmHg)', 
                                           validators=[Optional(), NumberRange(min=40, max=150)])
    heart_rate = IntegerField('Heart Rate (bpm)', 
                             validators=[Optional(), NumberRange(min=30, max=220)])
    temperature = FloatField('Body Temperature (°C)', 
                            validators=[Optional(), NumberRange(min=35, max=42)])
    oxygen_saturation = FloatField('Oxygen Saturation (%)', 
                                  validators=[Optional(), NumberRange(min=70, max=100)])
    
    # Physical activity
    steps = IntegerField('Steps Today', 
                        validators=[Optional(), NumberRange(min=0, max=100000)])
    exercise_duration = IntegerField('Exercise Duration (minutes)', 
                                    validators=[Optional(), NumberRange(min=0, max=1440)])
    calories_burned = IntegerField('Calories Burned', 
                                  validators=[Optional(), NumberRange(min=0, max=10000)])
    
    # Sleep data
    sleep_duration = FloatField('Sleep Duration (hours)', 
                               validators=[Optional(), NumberRange(min=0, max=24)])
    sleep_quality = IntegerField('Sleep Quality (1-10)', 
                                validators=[Optional(), NumberRange(min=1, max=10)])
    
    # Nutrition
    water_intake = FloatField('Water Intake (liters)', 
                             validators=[Optional(), NumberRange(min=0, max=10)])
    calorie_intake = IntegerField('Calorie Intake', 
                                 validators=[Optional(), NumberRange(min=0, max=10000)])
    
    # Mental health
    stress_level = IntegerField('Stress Level (1-10)', 
                               validators=[Optional(), NumberRange(min=1, max=10)])
    mood = SelectField('Mood', choices=[
        ('', 'Select...'),
        ('happy', 'Happy'), 
        ('energetic', 'Energetic'),
        ('calm', 'Calm'),
        ('neutral', 'Neutral'),
        ('tired', 'Tired'), 
        ('stressed', 'Stressed'),
        ('sad', 'Sad'),
        ('anxious', 'Anxious')
    ], validators=[Optional()])
    
    # Notes
    notes = TextAreaField('Notes', validators=[Optional()])
    
    submit = SubmitField('Save') 