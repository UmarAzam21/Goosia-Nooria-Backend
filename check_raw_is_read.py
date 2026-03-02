from database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# Run raw SQL to check is_read values
result = db.execute(text("SELECT id, sender_id, is_read FROM admin_messages LIMIT 5"))
rows = result.fetchall()

print('Raw SQL query results for is_read:')
for row in rows:
    print(f'  ID {row[0]}: sender_id={row[1]}, is_read={row[2]} (type={type(row[2]).__name__})')

# Also check what PostgreSQL thinks is_read actually is
result2 = db.execute(text("SELECT column_name, data_type, column_default FROM information_schema.columns WHERE table_name='admin_messages' AND column_name='is_read'"))
col_info = result2.fetchone()

if col_info:
    print(f'\nPostgreSQL column info for is_read:')
    print(f'  data_type: {col_info[1]}')
    print(f'  column_default: {col_info[2]}')

db.close()
