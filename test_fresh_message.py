from database import SessionLocal
from models import AdminMessage

db = SessionLocal()

try:
    # Delete all existing admin messages
    db.query(AdminMessage).delete()
    db.commit()
    print("✓ Deleted all admin messages")
    
    # Create a fresh test message with is_read explicitly False
    test_msg = AdminMessage(
        student_id=5,
        sender_id=1,  # Admin
        student_name="Ali Ahmed",
        message="Test message with explicit is_read=False",
        is_read=False,  # EXPLICITLY SET
        is_responded=False,
        recipient_type="student"
    )
    
    db.add(test_msg)
    db.commit()
    db.refresh(test_msg)
    
    print(f"Created message ID {test_msg.id}")
    print(f"After commit: is_read = {test_msg.is_read}")
    
    # Query it back
    queried = db.query(AdminMessage).filter(AdminMessage.id == test_msg.id).first()
    print(f"After query: is_read = {queried.is_read}")
    
    if queried.is_read == False:
        print("\n✓ SUCCESS: Message correctly marked as unread!")
    else:
        print(f"\n✗ PROBLEM: Message marked as is_read={queried.is_read} when it should be False")
        
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()
