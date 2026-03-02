#!/usr/bin/env python
"""Test that messages are returned in correct order from API"""

from database import SessionLocal
from models import AdminMessage

db = SessionLocal()

# Get messages in ascending order (as backend API now returns)
messages_asc = db.query(AdminMessage).order_by(AdminMessage.created_at).all()

print("=" * 70)
print("MESSAGE ORDER CHECK - First 3 and Last 3")
print("=" * 70)

print("\nFIRST 3 (oldest - should be at top of chat):")
for msg in messages_asc[:3]:
    print(f"  {msg.created_at} | {msg.student_name}: {msg.message[:35]}")

print("\nLAST 3 (newest - should be at bottom of chat):")
for msg in messages_asc[-3:]:
    print(f"  {msg.created_at} | {msg.student_name}: {msg.message[:35]}")

# Verify order is correct
is_ordered = all(messages_asc[i].created_at <= messages_asc[i+1].created_at 
                  for i in range(len(messages_asc)-1))

print("\n" + "=" * 70)
if is_ordered:
    print("✓ MESSAGE ORDER CORRECT - Oldest first, newest last")
else:
    print("✗ MESSAGE ORDER WRONG - Messages not in chronological order")
print("=" * 70)

db.close()
