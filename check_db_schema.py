import sqlite3

conn = sqlite3.connect('masjid.db')
cursor = conn.cursor()

# Get the CREATE TABLE statement
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='admin_messages'")
result = cursor.fetchone()

if result:
    print('admin_messages CREATE TABLE statement:')
    print(result[0])
else:
    print('Table not found')

# Also check a sample message
cursor.execute("SELECT id, student_id, sender_id, is_read FROM admin_messages LIMIT 1")
sample = cursor.fetchone()
if sample:
    print(f'\nSample message: id={sample[0]}, student_id={sample[1]}, sender_id={sample[2]}, is_read={sample[3]}')

conn.close()
