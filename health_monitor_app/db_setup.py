"""
Database setup script for the Health Monitor application.

This script initializes the metadata baselines for different demographics,
which will be used as reference data for user health metric comparisons.
"""
import json
import os
from datetime import datetime
from app import create_app, db
from app.models import MetadataBaseline, User

def create_baseline_data():
    """
    Create and initialize baseline health data for different demographics.
    
    This function populates the MetadataBaseline table with average values
    for different age groups and genders based on standard health metrics.
    """
    app = create_app()
    
    with app.app_context():
        # Check if baseline data already exists
        if MetadataBaseline.query.count() > 0:
            print("Baseline data already exists. Skipping initialization.")
            return
        
        print("Creating baseline data for different demographics...")
        
        # Define age groups
        age_groups = ["18-29", "30-39", "40-49", "50-59", "60-69", "70+"]
        
        # Define gender categories
        genders = ["male", "female"]
        
        # Define baseline data for weight (in kg)
        weight_baselines = {
            "male": {
                "18-29": {"avg": 75.0, "min": 60.0, "max": 90.0},
                "30-39": {"avg": 78.0, "min": 63.0, "max": 93.0},
                "40-49": {"avg": 80.0, "min": 65.0, "max": 95.0},
                "50-59": {"avg": 82.0, "min": 67.0, "max": 97.0},
                "60-69": {"avg": 80.0, "min": 65.0, "max": 95.0},
                "70+": {"avg": 77.0, "min": 62.0, "max": 92.0}
            },
            "female": {
                "18-29": {"avg": 62.0, "min": 50.0, "max": 74.0},
                "30-39": {"avg": 64.0, "min": 52.0, "max": 77.0},
                "40-49": {"avg": 66.0, "min": 53.0, "max": 79.0},
                "50-59": {"avg": 68.0, "min": 55.0, "max": 81.0},
                "60-69": {"avg": 67.0, "min": 54.0, "max": 80.0},
                "70+": {"avg": 65.0, "min": 52.0, "max": 78.0}
            }
        }
        
        # Define baseline data for heart rate (in bpm)
        heart_rate_baselines = {
            "male": {
                "18-29": {"avg": 70, "min": 60, "max": 100},
                "30-39": {"avg": 72, "min": 60, "max": 100},
                "40-49": {"avg": 74, "min": 60, "max": 100},
                "50-59": {"avg": 76, "min": 60, "max": 100},
                "60-69": {"avg": 78, "min": 60, "max": 100},
                "70+": {"avg": 80, "min": 60, "max": 100}
            },
            "female": {
                "18-29": {"avg": 74, "min": 60, "max": 100},
                "30-39": {"avg": 76, "min": 60, "max": 100},
                "40-49": {"avg": 78, "min": 60, "max": 100},
                "50-59": {"avg": 80, "min": 60, "max": 100},
                "60-69": {"avg": 82, "min": 60, "max": 100},
                "70+": {"avg": 84, "min": 60, "max": 100}
            }
        }
        
        # Define baseline data for blood pressure (systolic)
        blood_pressure_baselines = {
            "male": {
                "18-29": {"avg": 120, "min": 90, "max": 140},
                "30-39": {"avg": 122, "min": 90, "max": 140},
                "40-49": {"avg": 125, "min": 90, "max": 140},
                "50-59": {"avg": 127, "min": 90, "max": 140},
                "60-69": {"avg": 130, "min": 90, "max": 140},
                "70+": {"avg": 135, "min": 90, "max": 150}
            },
            "female": {
                "18-29": {"avg": 115, "min": 90, "max": 140},
                "30-39": {"avg": 118, "min": 90, "max": 140},
                "40-49": {"avg": 122, "min": 90, "max": 140},
                "50-59": {"avg": 125, "min": 90, "max": 140},
                "60-69": {"avg": 130, "min": 90, "max": 140},
                "70+": {"avg": 135, "min": 90, "max": 150}
            }
        }
        
        # Define baseline data for steps per day
        steps_baselines = {
            "male": {
                "18-29": {"avg": 9000, "min": 7000, "max": 12000},
                "30-39": {"avg": 8500, "min": 6500, "max": 11000},
                "40-49": {"avg": 8000, "min": 6000, "max": 10000},
                "50-59": {"avg": 7500, "min": 5500, "max": 9500},
                "60-69": {"avg": 6500, "min": 5000, "max": 8500},
                "70+": {"avg": 5500, "min": 4000, "max": 7500}
            },
            "female": {
                "18-29": {"avg": 8500, "min": 6500, "max": 11000},
                "30-39": {"avg": 8000, "min": 6000, "max": 10500},
                "40-49": {"avg": 7500, "min": 5500, "max": 10000},
                "50-59": {"avg": 7000, "min": 5000, "max": 9000},
                "60-69": {"avg": 6000, "min": 4500, "max": 8000},
                "70+": {"avg": 5000, "min": 3500, "max": 7000}
            }
        }
        
        # Define baseline data for sleep duration (in hours)
        sleep_baselines = {
            "male": {
                "18-29": {"avg": 7.5, "min": 7.0, "max": 9.0},
                "30-39": {"avg": 7.2, "min": 7.0, "max": 8.5},
                "40-49": {"avg": 7.0, "min": 6.5, "max": 8.0},
                "50-59": {"avg": 6.8, "min": 6.0, "max": 8.0},
                "60-69": {"avg": 6.5, "min": 5.5, "max": 7.5},
                "70+": {"avg": 6.2, "min": 5.0, "max": 7.0}
            },
            "female": {
                "18-29": {"avg": 7.8, "min": 7.0, "max": 9.0},
                "30-39": {"avg": 7.5, "min": 7.0, "max": 8.5},
                "40-49": {"avg": 7.2, "min": 6.5, "max": 8.0},
                "50-59": {"avg": 7.0, "min": 6.0, "max": 8.0},
                "60-69": {"avg": 6.8, "min": 5.5, "max": 7.5},
                "70+": {"avg": 6.5, "min": 5.0, "max": 7.0}
            }
        }
        
        # Define all baselines in a dictionary for easy iteration
        all_baselines = {
            "weight": weight_baselines,
            "heart_rate": heart_rate_baselines,
            "blood_pressure": blood_pressure_baselines,
            "steps": steps_baselines,
            "sleep_duration": sleep_baselines
        }
        
        # Create baseline records for each metric, gender and age group
        baseline_records = []
        
        for metric, gender_data in all_baselines.items():
            for gender, age_data in gender_data.items():
                for age_group, values in age_data.items():
                    # Create additional metadata including percentiles
                    metadata = {
                        "percentile_25": values["min"] + (values["avg"] - values["min"]) * 0.5,
                        "percentile_75": values["avg"] + (values["max"] - values["avg"]) * 0.5,
                        "standard_deviation": (values["max"] - values["min"]) / 4.0,
                        "sample_size": 1000,  # Fictional sample size
                        "last_updated": datetime.utcnow().isoformat()
                    }
                    
                    baseline = MetadataBaseline(
                        gender=gender,
                        age_group=age_group,
                        metric_type=metric,
                        avg_value=values["avg"],
                        min_value=values["min"],
                        max_value=values["max"],
                        metadata_json=json.dumps(metadata)
                    )
                    baseline_records.append(baseline)
        
        # Add all records to the database
        try:
            db.session.add_all(baseline_records)
            db.session.commit()
            print(f"Successfully added {len(baseline_records)} baseline records.")
        except Exception as e:
            db.session.rollback()
            print(f"Error adding baseline data: {str(e)}")

if __name__ == "__main__":
    create_baseline_data() 