#!/usr/bin/env python3
"""
Create Teacher records for all teacher users
"""
from database import SessionLocal
from models import User, Teacher

db = SessionLocal()

print("=" * 80)
print("CREATING TEACHER PROFILES FOR ALL TEACHER USERS")
print("=" * 80)

# Get all teacher users
teacher_users = db.query(User).filter(User.role == 'teacher').all()

print(f"\n📋 Found {len(teacher_users)} teacher users")

# Check existing teacher records
existing_teachers = db.query(Teacher).all()
teacher_user_ids = {t.user_id for t in existing_teachers}

print(f"📋 Found {len(existing_teachers)} existing teacher records")

# Create missing teacher records
missing_teachers = [u for u in teacher_users if u.id not in teacher_user_ids]

if missing_teachers:
    print(f"\n👨‍🏫 Creating {len(missing_teachers)} missing teacher record(s):")
    
    for user in missing_teachers:
        teacher = Teacher(
            user_id=user.id,
            bio="",
            experience_years=0,
            qualification="",
            is_available=True
        )
        db.add(teacher)
        print(f"   ✅ {user.email}")
    
    db.commit()
    print(f"\n✅ All {len(missing_teachers)} teacher record(s) created successfully!")
else:
    print(f"\n✅ All teacher users already have teacher records!")

# Show all teachers now
print("\n" + "=" * 80)
print("📊 ALL TEACHER PROFILES:")
print("=" * 80)

all_teachers = db.query(Teacher).all()
for t in all_teachers:
    print(f"\n👨‍🏫 {t.user.email}")
    print(f"   ID: {t.id}")
    print(f"   User ID: {t.user_id}")
    print(f"   Available: {t.is_available}")

db.close()

print("\n✨ Teacher profiles are ready for assigning time slots!")
