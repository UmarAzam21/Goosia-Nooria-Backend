from database import SessionLocal
from models import TimeSlot, Teacher
from datetime import time

db = SessionLocal()

print("=" * 80)
print("ADDING DAILY TIME SLOTS FOR ALL TEACHERS")
print("=" * 80)

# Get all teachers
teachers = db.query(Teacher).all()

if not teachers:
    print("❌ No teachers found in the database")
    db.close()
    exit(1)

print(f"\n📋 Found {len(teachers)} teacher(s)")

# Time slots to add: Morning 6-7 AM and Night 9-10 PM
time_slots_data = [
    {"name": "Morning", "start": time(6, 0), "end": time(7, 0)},
    {"name": "Night", "start": time(21, 0), "end": time(22, 0)},  # 9 PM - 10 PM in 24-hour format
]

# Days of week
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

try:
    for teacher in teachers:
        print(f"\n👨‍🏫 Teacher ID {teacher.id} ({teacher.user.email}):")
        
        # Delete existing time slots for this teacher
        existing_slots = db.query(TimeSlot).filter(TimeSlot.teacher_id == teacher.id).all()
        print(f"   Removing {len(existing_slots)} existing time slots...")
        for slot in existing_slots:
            db.delete(slot)
        db.commit()
        
        # Add new time slots for each day
        added_count = 0
        for time_slot in time_slots_data:
            for day in days:
                new_slot = TimeSlot(
                    teacher_id=teacher.id,
                    day_of_week=day,
                    start_time=time_slot["start"],
                    end_time=time_slot["end"],
                    is_available=True
                )
                db.add(new_slot)
                added_count += 1
        
        db.commit()
        print(f"   ✅ Added {added_count} new time slots")
        print(f"      - Morning: 6:00 AM - 7:00 AM (All 7 days)")
        print(f"      - Night: 9:00 PM - 10:00 PM (All 7 days)")
    
    print("\n" + "=" * 80)
    print("✅ TIME SLOTS CONFIGURED SUCCESSFULLY")
    print("=" * 80)
    
    # Show summary
    print("\n📊 TIME SLOTS SUMMARY:")
    for teacher in teachers:
        slots = db.query(TimeSlot).filter(TimeSlot.teacher_id == teacher.id).all()
        
        # Group by time
        times = {}
        for slot in slots:
            time_key = f"{slot.start_time.strftime('%H:%M')} - {slot.end_time.strftime('%H:%M')}"
            if time_key not in times:
                times[time_key] = []
            times[time_key].append(slot.day_of_week)
        
        print(f"\n👨‍🏫 {teacher.user.email}:")
        for time_key, days_list in sorted(times.items()):
            if len(set(days_list)) == 7:
                print(f"   ✅ {time_key}: All Days (Mon-Sun)")
            else:
                print(f"   ✅ {time_key}: {', '.join(sorted(set(days_list)))}")
    
    print("\n✨ Daily time slots are ready!")
    print("   Students can enroll in 6-7 AM or 9-10 PM classes any day of the week")

except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
