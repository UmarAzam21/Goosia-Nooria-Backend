from database import SessionLocal
from models import TimeSlot, Enrollment, Payment, ChatMessage, Class

db = SessionLocal()
try:
    # Delete dependent data first
    db.query(Class).delete()
    db.query(ChatMessage).delete()
    db.query(Payment).delete()
    db.query(Enrollment).delete()
    db.query(TimeSlot).delete()
    db.commit()
    
    # Add fresh time slots: one morning, one afternoon, one evening per teacher
    from datetime import time
    
    new_slots = [
        # Teacher 1
        {'teacher_id': 1, 'day_of_week': 'Monday', 'start_time': time(9, 0), 'end_time': time(10, 0)},
        {'teacher_id': 1, 'day_of_week': 'Tuesday', 'start_time': time(14, 0), 'end_time': time(15, 0)},
        {'teacher_id': 1, 'day_of_week': 'Wednesday', 'start_time': time(21, 0), 'end_time': time(22, 0)},
        
        # Teacher 2
        {'teacher_id': 2, 'day_of_week': 'Thursday', 'start_time': time(9, 0), 'end_time': time(10, 0)},
        {'teacher_id': 2, 'day_of_week': 'Friday', 'start_time': time(14, 0), 'end_time': time(15, 0)},
        {'teacher_id': 2, 'day_of_week': 'Saturday', 'start_time': time(17, 0), 'end_time': time(18, 0)},
        
        # Teacher 3
        {'teacher_id': 3, 'day_of_week': 'Sunday', 'start_time': time(10, 0), 'end_time': time(11, 0)},
        {'teacher_id': 3, 'day_of_week': 'Monday', 'start_time': time(15, 0), 'end_time': time(16, 0)},
        {'teacher_id': 3, 'day_of_week': 'Tuesday', 'start_time': time(20, 0), 'end_time': time(21, 0)},
    ]
    
    for slot_data in new_slots:
        slot = TimeSlot(**slot_data)
        db.add(slot)
    
    db.commit()
    print('✓ Reset time slots - 3 options per teacher')
    print('\nTeacher Ahmed:    09:00-10:00 AM, 14:00-15:00 (2-3 PM), 21:00-22:00 (9-10 PM)')
    print('Teacher Fatima:   09:00-10:00 AM, 14:00-15:00 (2-3 PM), 17:00-18:00 (5-6 PM)')
    print('Teacher Ibrahim:  10:00-11:00 AM, 15:00-16:00 (3-4 PM), 20:00-21:00 (8-9 PM)')
except Exception as e:
    print(f'Error: {e}')
    db.rollback()
finally:
    db.close()
