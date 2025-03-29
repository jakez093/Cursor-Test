from app import create_app, db
from app.models import User, HealthData

def check_health_data():
    app = create_app()
    
    with app.app_context():
        # Get all users
        users = User.query.all()
        
        for user in users:
            # Count health records for each user
            record_count = HealthData.query.filter_by(user_id=user.id).count()
            
            # Get some sample records
            recent_records = HealthData.query.filter_by(user_id=user.id).order_by(HealthData.date.desc()).limit(5).all()
            
            print(f"User: {user.username}")
            print(f"Total health records: {record_count}")
            
            if recent_records:
                print("Most recent records:")
                for i, record in enumerate(recent_records):
                    print(f"  {i+1}. Date: {record.date.strftime('%Y-%m-%d %H:%M')}")
                    print(f"     Weight: {record.weight} kg")
                    print(f"     BP: {record.blood_pressure_systolic}/{record.blood_pressure_diastolic} mmHg")
                    print(f"     Heart Rate: {record.heart_rate} bpm")
                    print(f"     Steps: {record.steps}")
                    print(f"     Sleep: {record.sleep_duration} hours (quality: {record.sleep_quality}/10)")
                    print()

if __name__ == "__main__":
    check_health_data() 