"""
Test multiple messages directly in database to verify they're not being replaced
"""
from database import SessionLocal
from models import User, AdminMessage
from datetime import datetime

def test_multiple_messages():
    db = SessionLocal()
    try:
        print("=== CHECKING DATABASE FOR ADMIN MESSAGE DATA ===")
        
        # Find a student
        students = db.query(User).filter(User.role == "student").all()
        if not students:
            print("No students found in database")
            return
        
        student = students[0]
        print(f"✅ Found student: {student.name} (ID={student.id}, Email={student.email})")
        
        # Check existing messages for this student
        existing_messages = db.query(AdminMessage).filter(
            AdminMessage.student_id == student.id
        ).all()
        print(f"\n📊 Existing messages from this student: {len(existing_messages)}")
        if existing_messages:
            print("Existing messages:")
            for msg in existing_messages[-5:]:
                print(f"  ID={msg.id}, Message='{msg.message}'")
        
        # Clear old test messages for this student (optional)
        # db.query(AdminMessage).filter(AdminMessage.student_id == student.id).delete()
        # db.commit()
        
        # Create 3 new messages
        print(f"\n=== CREATING 3 TEST MESSAGES ===")
        for i in range(1, 4):
            msg = AdminMessage(
                student_id=student.id,
                student_name=student.name,
                message=f"Test message number {i} - This is test message {i}",
                recipient_type="admin"
            )
            db.add(msg)
            db.flush()  # Flush to get the ID
            print(f"Created message {i}: ID={msg.id}, Text='{msg.message}'")
        
        db.commit()
        print("✅ All messages committed to database")
        
        # Now query them back
        print(f"\n=== QUERYING ALL MESSAGES FOR STUDENT {student.id} ===")
        messages = db.query(AdminMessage).filter(
            AdminMessage.student_id == student.id
        ).order_by(AdminMessage.created_at).all()
        
        print(f"Total messages found: {len(messages)}")
        print("Messages by ID:")
        for msg in messages:
            print(f"  ID={msg.id}, Created={msg.created_at}, Message='{msg.message[:40]}'")
        
        # Check if we have 3 distinct new messages
        print(f"\n=== VERIFICATION ===")
        test_messages = [m for m in messages if "Test message number" in m.message]
        print(f"Test messages found: {len(test_messages)}")
        if len(test_messages) >= 3:
            print("✅ All 3 test messages are present and distinct")
            for msg in test_messages[-3:]:
                print(f"  ID={msg.id}: {msg.message}")
        else:
            print(f"⚠️  Only {len(test_messages)} test messages found (expected 3)")
        
        # Check for duplicates by ID
        ids = [m.id for m in messages]
        unique_ids = set(ids)
        if len(ids) != len(unique_ids):
            print(f"⚠️  DUPLICATE IDs: {len(ids)} messages, {len(unique_ids)} unique")
        else:
            print(f"✅ All message IDs are unique ({len(unique_ids)} total)")
            
    finally:
        db.close()

if __name__ == "__main__":
    test_multiple_messages()
