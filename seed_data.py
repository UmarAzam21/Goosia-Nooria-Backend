"""Seed script to populate database with initial data"""
from datetime import datetime, time
from database import SessionLocal
from models import User, Course, Teacher, TimeSlot, UserRole
from auth import get_password_hash

def seed_database():
    db = SessionLocal()
    
    try:
        print("Starting database seeding...")
        
        # Create Admin User
        admin = User(
            name="Admin User",
            email="admin@masjid.com",
            password_hash=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            phone="+1234567890"
        )
        db.add(admin)
        db.commit()
        print("✓ Admin user created")
        
        # Create Courses
        courses_data = [
            {
                "name": "Nazra Quran",
                "description": "Learn to read Quran from basic Qaida to complete recitation",
                "duration_weeks": 4,  # Monthly course (4 weeks)
                "fee": 2000.00
            }
        ]
        
        courses = []
        for course_data in courses_data:
            course = Course(**course_data)
            db.add(course)
            courses.append(course)
        
        db.commit()
        print(f"✓ {len(courses)} courses created")
        
        # Create Teacher Users
        teachers_data = [
            {
                "name": "Sheikh Ahmed Ali",
                "email": "ahmed@masjid.com",
                "phone": "+1234567891",
                "bio": "10+ years of Quran teaching experience with Ijazah",
                "experience_years": 12,
                "qualification": "Ijazah in Quran Recitation, BA Islamic Studies"
            },
            {
                "name": "Ustadh Fatima Hassan",
                "email": "fatima@masjid.com",
                "phone": "+1234567892",
                "bio": "Specialist in Tajweed and Quranic Arabic",
                "experience_years": 8,
                "qualification": "Masters in Tajweed, Certified Quran Teacher"
            },
            {
                "name": "Sheikh Muhammad Ibrahim",
                "email": "ibrahim@masjid.com",
                "phone": "+1234567893",
                "bio": "Scholar of Hadith and Islamic Jurisprudence",
                "experience_years": 15,
                "qualification": "PhD Islamic Jurisprudence, Hadith Scholar"
            }
        ]
        
        teacher_profiles = []
        for i, teacher_data in enumerate(teachers_data):
            # Create user
            user = User(
                name=teacher_data["name"],
                email=teacher_data["email"],
                password_hash=get_password_hash("teacher123"),
                role=UserRole.TEACHER,
                phone=teacher_data.get("phone")
            )
            db.add(user)
            db.flush()
            
            # Create teacher profile (assign to courses)
            # All teachers assigned to Nazra Quran course
            course_id = courses[0].id
            
            teacher = Teacher(
                user_id=user.id,
                course_id=course_id,
                bio=teacher_data["bio"],
                experience_years=teacher_data["experience_years"],
                qualification=teacher_data["qualification"]
            )
            db.add(teacher)
            teacher_profiles.append(teacher)
        
        db.commit()
        print(f"✓ {len(teacher_profiles)} teachers created")
        
        # Create Time Slots for each teacher
        # Each teacher will have all 3 time slot options
        time_slots_data = [
            # Morning slot (9-10 AM)
            {"day_of_week": "Monday", "start_time": time(9, 0), "end_time": time(10, 0)},
            
            # Afternoon slot (2-3 PM)
            {"day_of_week": "Tuesday", "start_time": time(14, 0), "end_time": time(15, 0)},
            
            # Evening slot (9-10 PM)
            {"day_of_week": "Wednesday", "start_time": time(21, 0), "end_time": time(22, 0)},
        ]
        
        slot_count = 0
        for teacher in teacher_profiles:
            # Assign all 3 time slots to each teacher
            for slot_data in time_slots_data:
                time_slot = TimeSlot(
                    teacher_id=teacher.id,
                    **slot_data
                )
                db.add(time_slot)
                slot_count += 1
        
        db.commit()
        print(f"✓ {slot_count} time slots created")
        
        # Create Sample Students
        students_data = [
            {"name": "Ali Rahman", "email": "ali@student.com"},
            {"name": "Sara Ahmed", "email": "sara@student.com"},
            {"name": "Omar Malik", "email": "omar@student.com"},
        ]
        
        for student_data in students_data:
            student = User(
                name=student_data["name"],
                email=student_data["email"],
                password_hash=get_password_hash("student123"),
                role=UserRole.STUDENT
            )
            db.add(student)
        
        db.commit()
        print(f"✓ {len(students_data)} sample students created")
        
        print("\n=== Database seeded successfully! ===\n")
        print("Login Credentials:")
        print("-" * 40)
        print("Admin:")
        print("  Email: admin@masjid.com")
        print("  Password: admin123")
        print("\nTeachers:")
        print("  Email: ahmed@masjid.com, fatima@masjid.com, ibrahim@masjid.com")
        print("  Password: teacher123")
        print("\nStudents:")
        print("  Email: ali@student.com, sara@student.com, omar@student.com")
        print("  Password: student123")
        print("-" * 40)
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
