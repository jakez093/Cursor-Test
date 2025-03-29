"""
Script to create a test user for the Health Monitor application.
This utility creates a default user account in the database if no users exist,
allowing for immediate testing of the application.
"""
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

def create_test_user():
    """
    Create a test user in the database if none exists.
    
    Checks if any users are present in the database and creates a default test user
    with predefined credentials if none found. Otherwise, lists all existing users.
    """
    app = create_app()
    
    with app.app_context():
        # Check if any users exist
        user_count = User.query.count()
        
        if user_count == 0:
            print("No users found. Creating a test user...")
            # Create a test user
            test_user = User(
                username="testuser",
                email="test@example.com",
                password_hash=generate_password_hash("9wTh$7xR2pL#8kQ!4vZ@5mN*6gB&3eD")
            )
            
            db.session.add(test_user)
            db.session.commit()
            
            print(f"Created test user: {test_user.username} (email: {test_user.email}, password: password123)")
        else:
            print(f"Users already exist in the database. Total users: {user_count}")
            users = User.query.all()
            for user in users:
                print(f"  - {user.username} (email: {user.email})")

if __name__ == "__main__":
    create_test_user() 