"""Add notifications table to database"""
from database import SessionLocal, engine
from models import Base, Notification

def add_notifications_table():
    """Create notifications table"""
    print("Adding notifications table...")
    
    # Create only the notifications table
    Notification.__table__.create(engine, checkfirst=True)
    
    print("✓ Notifications table created successfully!")

if __name__ == "__main__":
    add_notifications_table()
