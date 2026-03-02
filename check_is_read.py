from database import SessionLocal
from sqlalchemy import inspect
from models import AdminMessage

db = SessionLocal()
inspector = inspect(db.bind)

columns = inspector.get_columns('admin_messages')

print('admin_messages columns:')
for col in columns:
    print(f'  name: {col["name"]}')
    print(f'    type: {col["type"]}')
    print(f'    nullable: {col["nullable"]}')
    print(f'    default: {col["default"]}')
    print()

# Also check what value is_read currently has in the database
messages = db.query(AdminMessage).limit(5).all()
print(f'\nFirst 5 messages is_read values:')
for msg in messages:
    print(f'  Message ID {msg.id}: is_read={msg.is_read} (type={type(msg.is_read).__name__})')

db.close()
