#!/usr/bin/env python3
"""
Clean database for client demo - Nuclear option
Drop everything and create fresh clean data
"""

from database import SessionLocal, engine
from models import Base, User
from sqlalchemy.orm import sessionmaker
from auth import get_password_hash  # Use the same hashing function as auth.py

print("=" * 80)
print("NUCLEAR CLEANUP - DROPPING ALL TABLES AND RECREATING")
print("=" * 80)

print("\n🔄 Dropping all tables...")
Base.metadata.drop_all(bind=engine)
print("   ✅ All tables dropped")

print("\n🔄 Recreating database schema...")
Base.metadata.create_all(bind=engine)
print("   ✅ Schema recreated")

print("\n🔄 Creating clean demo data...")
Session = sessionmaker(bind=engine)
db = Session()

# Create users
print("\n   Creating users...")

# Admin
admin = User(
    email="admin@masjid.com",
    password_hash=get_password_hash("admin123"),
    name="Administrator",
    role="admin",
    phone="+1234567890"
)
db.add(admin)

# Teachers
teacher1 = User(
    email="ahmed@masjid.com",
    password_hash=get_password_hash("ahmed123"),
    name="Ahmed Khan",
    role="teacher",
    phone="+1234567891"
)
db.add(teacher1)

teacher2 = User(
    email="fatima@masjid.com",
    password_hash=get_password_hash("fatima123"),
    name="Fatima Ahmed",
    role="teacher",
    phone="+1234567892"
)
db.add(teacher2)

teacher3 = User(
    email="ibrahim@masjid.com",
    password_hash=get_password_hash("ibrahim123"),
    name="Ibrahim Ali",
    role="teacher",
    phone="+1234567893"
)
db.add(teacher3)

# Student
student = User(
    email="ali@student.com",
    password_hash=get_password_hash("ali123"),
    name="Ali Hassan",
    role="student",
    phone="+1234567894"
)
db.add(student)

db.commit()

print("   ✅ Users created:")
print(f"      - 1 Admin: admin@masjid.com")
print(f"      - 3 Teachers: ahmed@, fatima@, ibrahim@")
print(f"      - 1 Student: ali@student.com")

print("\n" + "=" * 80)
print("✅ DATABASE CLEANED AND RESET FOR CLIENT DEMO")
print("=" * 80)

print("\n📋 CREDENTIALS FOR TESTING:")
print("""
Admin:
  Email: admin@masjid.com
  Password: admin123

Teachers:
  1. ahmed@masjid.com / ahmed123
  2. fatima@masjid.com / fatima123
  3. ibrahim@masjid.com / ibrahim123

Student:
  ali@student.com / ali123
""")

print("\n✨ Ready for client demo!")
db.close()
