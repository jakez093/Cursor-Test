import sys
import os
import random
from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, HealthData

def get_mood_for_stress_level(stress_level):
    """Select appropriate mood based on stress level"""
    if stress_level <= 3:
        return random.choice(['happy', 'calm', 'energetic'])
    elif stress_level <= 6:
        return random.choice(['neutral', 'calm', 'happy', 'tired'])
    else:
        return random.choice(['stressed', 'tired', 'anxious'])

def generate_record(user_id, record_date, i, weight, systolic, diastolic, 
                   heart_rate, steps, sleep_duration, water_intake, calorie_intake,
                   stress_level):
    """Generate a single health record with the given parameters"""
    # Check if weekend
    is_weekend = record_date.weekday() >= 5
    weekend_factor = 1.2 if is_weekend else 1.0
    
    # Add natural variation
    weight_change = random.uniform(-0.5, 0.5)
    
    # Calculate metrics with trends
    weight = max(68.0, min(80.0, weight - 0.08 + weight_change))
    
    systolic = max(110, min(140, systolic + random.randint(-5, 5)))
    diastolic = max(70, min(95, diastolic + random.randint(-3, 3)))
    
    heart_rate = max(60, min(85, heart_rate + random.randint(-3, 3)))
    if not is_weekend:
        heart_rate = max(60, heart_rate - random.randint(0, 3))
    
    steps_base = steps + random.randint(-1000, 1000)
    steps = max(4000, min(12000, steps_base * (1.0/weekend_factor)))
    
    sleep_change = random.uniform(-0.5, 0.5)
    sleep_duration = max(5.0, min(9.0, sleep_duration + sleep_change + 
                          (0.5 if is_weekend else -0.1)))
    
    water_intake = max(1.0, min(3.0, water_intake + random.uniform(-0.3, 0.3)))
    
    calorie_intake = max(1600, min(2800, calorie_intake + random.randint(-150, 150) + 
                           (200 if is_weekend else 0)))
    
    stress_factor = -1 if is_weekend else 1
    stress_level = max(1, min(10, stress_level + random.randint(-1, 1) + stress_factor))
    
    mood = get_mood_for_stress_level(stress_level)
    
    # Create record
    return HealthData(
        user_id=user_id,
        date=record_date,
        weight=round(weight, 1),
        blood_pressure_systolic=systolic,
        blood_pressure_diastolic=diastolic,
        heart_rate=heart_rate,
        temperature=round(36.5 + random.uniform(-0.3, 0.5), 1),
        oxygen_saturation=round(97.0 + random.uniform(-1.0, 2.0), 1),
        steps=int(steps),
        exercise_duration=int(steps / 1000 * 10),
        calories_burned=int(steps / 20),
        sleep_duration=round(sleep_duration, 1),
        sleep_quality=10 - int(stress_level),
        water_intake=round(water_intake, 1),
        calorie_intake=int(calorie_intake),
        stress_level=stress_level,
        mood=mood,
        notes=f"Day {i+1}: {'Weekend' if is_weekend else 'Weekday'} record."
    )

def create_dummy_data():
    """
    Add 25 health records for an existing user over a 1-month period
    """
    try:
        app = create_app()
        
        with app.app_context():
            # Get the first user in the database
            user = User.query.first()
            
            if not user:
                print("No users found in the database. Please create a user first.")
                return
            
            print(f"Adding dummy data for user: {user.username}")
            
            # Delete existing data for clean testing
            HealthData.query.filter_by(user_id=user.id).delete()
            db.session.commit()
            print("Cleared existing health data for user.")
            
            # Generate data for the past month (25 records)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            interval = (end_date - start_date) / 25
            
            # Initial values
            weight = random.uniform(70.0, 75.0)
            systolic = random.randint(115, 125)
            diastolic = random.randint(75, 85)
            heart_rate = random.randint(65, 75)
            steps = random.randint(7000, 9000)
            sleep_duration = random.uniform(6.5, 8.0)
            water_intake = random.uniform(1.5, 2.5)
            calorie_intake = random.randint(1800, 2200)
            stress_level = random.randint(3, 7)
            
            print("Generating 25 records...")
            
            # Generate records
            for i in range(25):
                record_date = start_date + (interval * i)
                
                health_data = generate_record(
                    user.id, record_date, i, weight, systolic, diastolic,
                    heart_rate, steps, sleep_duration, water_intake, 
                    calorie_intake, stress_level
                )
                
                db.session.add(health_data)
                print(f"Added record {i+1}/25 - Date: {record_date.strftime('%Y-%m-%d %H:%M')}")
            
            print("Committing records to database...")
            db.session.commit()
            
            print(f"Successfully added 25 health records over a 1-month period for {user.username}")
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_dummy_data() 