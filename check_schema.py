#!/usr/bin/env python3
"""Check database schema"""
import sys
sys.path.insert(0, '/c/Users/lenovo/Desktop/noori/backend')

from sqlalchemy import inspect
from database import engine

inspector = inspect(engine)

# Get column info for admin_messages table
print("\n" + "="*70)
print("ADMIN_MESSAGES TABLE SCHEMA")
print("="*70 + "\n")

columns = inspector.get_columns('admin_messages')
for col in columns:
    if col['name'] == 'is_read':
        print(f"Column: {col['name']}")
        print(f"  Type: {col['type']}")
        print(f"  Nullable: {col['nullable']}")
        print(f"  Default: {col['default']}")
        print(f"  Server Default: {col['server_default']}")
        print()

# Also check the table directly with SQL
print("="*70)
print("TABLE CREATE STATEMENT (via SQL)")
print("="*70 + "\n")

from database import SessionLocal
db = SessionLocal()

try:
    # Try to get schema info
    result = db.execute("PRAGMA table_info(admin_messages)")
    rows = result.fetchall()
    
    for row in rows:
        if 'is_read' in str(row):
            print(row)
except Exception as e:
    print(f"Error: {e}")

db.close()
print("\n" + "="*70 + "\n")
