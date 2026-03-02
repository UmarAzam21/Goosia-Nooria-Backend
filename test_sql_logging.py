import logging
from sqlalchemy import event
from database import SessionLocal, engine
from models import AdminMessage

# Enable SQLAlchemy logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

db = SessionLocal()

try:
    # Create a message
    msg = AdminMessage(
        student_id=5,
        sender_id=1,
        student_name="Ali Ahmed",
        message="Test message with SQL logging",
        is_read=False,
        is_responded=False,
        recipient_type="student"
    )
    
    print("\n>>> Adding message to session...")
    db.add(msg)
    
    print("\n>>> Committing...")
    db.commit()
    
    print(f"\n>>> After commit: is_read={msg.is_read}")
    
    print("\n>>> Refreshing...")
    db.refresh(msg)
    
    print(f"\n>>> After refresh: is_read={msg.is_read}")
    
    # Query it back
    print("\n>>> Querying message from DB...")
    queried = db.query(AdminMessage).filter(AdminMessage.id == msg.id).first()
    
    print(f"\n>>> Queried: is_read={queried.is_read}")
    
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()
