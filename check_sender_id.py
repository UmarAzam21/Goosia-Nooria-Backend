from database import SessionLocal
from models import AdminMessage
from sqlalchemy import inspect

db = SessionLocal()

# Get the last few messages with ALL fields
messages = db.query(AdminMessage).order_by(AdminMessage.id.desc()).limit(10).all()

print('=' * 100)
print('DETAILED MESSAGE CHECK')
print('=' * 100)
for msg in reversed(messages):
    sender_str = str(msg.sender_id) if msg.sender_id else 'NONE'
    print(f'ID:{msg.id:2d} | Student:{msg.student_id:2d} | Sender:{sender_str:5s} | Message: {msg.message[:40]}')

# Check if the column exists in the table schema
inspector = inspect(AdminMessage)
cols = [c.name for c in inspector.columns]
print('\n' + '=' * 100)
print('TABLE COLUMNS:')
for col in cols:
    print(f'  - {col}')
print('=' * 100)
print(f'sender_id in columns: {"sender_id" in cols}')

db.close()
