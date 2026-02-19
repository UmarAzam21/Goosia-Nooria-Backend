"""
Clean seed data script - Creates only 1 admin and 3 teachers
Removes all course, enrollment, payment, and student data
"""

from database import SessionLocal
from models import (
    User, Teacher, UserRole, TimeSlot, 
    Enrollment, Payment, ChatMessage, Notification, Course,
    Class, NotificationPreference
)
from auth import get_password_hash
from datetime import time

db = SessionLocal()

try:
    # Delete all data in order (respecting foreign keys)
    print("Cleaning up database...")
    db.query(Notification).delete()
    db.query(ChatMessage).delete()
    db.query(Class).delete()
    db.query(Payment).delete()
    db.query(Enrollment).delete()
    db.query(TimeSlot).delete()
    db.query(Teacher).delete()
    db.query(Course).delete()
    db.query(NotificationPreference).delete()
    db.query(User).delete()
    db.commit()
    print("Database cleaned successfully")

    # Create 1 Admin
    admin = User(
        name="Admin Noori",
        email="admin@noori.com",
        password_hash=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        phone="+92300000000",
        country="Pakistan",
        city="Karachi",
        timezone="Asia/Karachi",
        frozen_by_admin=False
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    print(f"Admin created: {admin.email} (ID: {admin.id})")

    # Create 3 Teachers with profiles
    teachers_data = [
        {
            "name": "Ustadh Ahmed",
            "email": "teacher1@noori.com",
            "password": "teacher123",
            "phone": "+92301111111",
            "bio": "Expert Quran teacher",
            "experience": 10,
            "qualification": "Hafiz-e-Quran"
        },
        {
            "name": "Ustadh Fatima",
            "email": "teacher2@noori.com",
            "password": "teacher123",
            "phone": "+92302222222",
            "bio": "Islamic studies specialist",
            "experience": 8,
            "qualification": "Masters Islamic Studies"
        },
        {
            "name": "Ustadh Hassan",
            "email": "teacher3@noori.com",
            "password": "teacher123",
            "phone": "+92303333333",
            "bio": "Arabic language instructor",
            "experience": 12,
            "qualification": "PhD Arabic Literature"
        }
    ]

    for teacher_data in teachers_data:
        teacher_user = User(
            name=teacher_data["name"],
            email=teacher_data["email"],
            password_hash=get_password_hash(teacher_data["password"]),
            role=UserRole.TEACHER,
            phone=teacher_data["phone"],
            country="Pakistan",
            city="Karachi",
            timezone="Asia/Karachi",
            frozen_by_admin=False
        )
        db.add(teacher_user)
        db.commit()
        db.refresh(teacher_user)

        # Create teacher profile
        teacher_profile = Teacher(
            user_id=teacher_user.id,
            bio=teacher_data["bio"],
            experience_years=teacher_data["experience"],
            qualification=teacher_data["qualification"],
            is_available=True
        )
        db.add(teacher_profile)
        db.commit()
        db.refresh(teacher_profile)

        # Create default time slots for teacher
        time_slots = [
            {"day": "Monday", "start": time(9, 0), "end": time(11, 0)},
            {"day": "Monday", "start": time(11, 0), "end": time(13, 0)},
            {"day": "Wednesday", "start": time(14, 0), "end": time(16, 0)},
            {"day": "Wednesday", "start": time(16, 0), "end": time(18, 0)},
            {"day": "Friday", "start": time(9, 0), "end": time(11, 0)},
            {"day": "Friday", "start": time(11, 0), "end": time(13, 0)},
            {"day": "Saturday", "start": time(14, 0), "end": time(16, 0)},
            {"day": "Saturday", "start": time(16, 0), "end": time(18, 0)},
        ]

        for slot in time_slots:
            time_slot = TimeSlot(
                teacher_id=teacher_profile.id,
                day_of_week=slot["day"],
                start_time=slot["start"],
                end_time=slot["end"],
                is_available=True
            )
            db.add(time_slot)

        db.commit()
        print(f"Teacher created: {teacher_user.email} (ID: {teacher_user.id})")
        print(f"  - Bio: {teacher_data['bio']}")
        print(f"  - 8 time slots created")

    print("\n✓ Database setup complete!")
    print("\nDemo Credentials:")
    print("─" * 50)
    print("ADMIN:")
    print(f"  Email: admin@noori.com")
    print(f"  Password: admin123")
    print("\nTEACHERS:")
    print(f"  Email: teacher1@noori.com | Password: teacher123")
    print(f"  Email: teacher2@noori.com | Password: teacher123")
    print(f"  Email: teacher3@noori.com | Password: teacher123")
    print("─" * 50)

except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()
