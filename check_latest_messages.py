from database import SessionLocal
from models import AdminMessage

db = SessionLocal()

# Get the last 5 messages
recent = db.query(AdminMessage).order_by(AdminMessage.id.desc()).limit(5).all()

print('=' * 70)
print('LAST 5 MESSAGES IN DATABASE')
print('=' * 70)
for msg in recent:
    print(f'ID: {msg.id:2d} | Student: {msg.student_name:15s} | Message: {msg.message}')
    print(f'        Is_Responded: {msg.is_responded} | Created: {msg.created_at}')
    print()

db.close()
