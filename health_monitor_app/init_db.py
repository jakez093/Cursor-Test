"""
Initialize the database for the Health Monitor application.

This script creates all the necessary database tables based on the models.
"""
from app import create_app, db

def init_db():
    """Initialize the database by creating all tables."""
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")

if __name__ == "__main__":
    init_db() 