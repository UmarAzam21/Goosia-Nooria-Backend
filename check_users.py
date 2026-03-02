#!/usr/bin/env python3
"""
Check available test users in the database
"""
import sqlite3

conn = sqlite3.connect('app.db')
cursor = conn.cursor()

# Get all users
print("\n📋 Users in database:")
print("=" * 60)
cursor.execute("SELECT id, email, role, name FROM users LIMIT 10")
for row in cursor.fetchall():
    uid, email, role, name = row
    print(f"ID: {uid:3} | Email: {email:30} | Role: {role:10} | Name: {name}")

print("\n" + "=" * 60)
conn.close()
