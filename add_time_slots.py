from database import SessionLocal
from models import TimeSlot
from datetime import time

db = SessionLocal()
try:
    # Add missing slots for each teacher
    new_slots = [
        # Teacher 1 - add Afternoon (2-3 PM) and Evening (9-10 PM)
        {'teacher_id': 1, 'day_of_week': 'Tuesday', 'start_time': time(14, 0), 'end_time': time(15, 0)},
        {'teacher_id': 1, 'day_of_week': 'Wednesday', 'start_time': time(21, 0), 'end_time': time(22, 0)},
        
        # Teacher 2 - add Morning (9-10 AM) and Afternoon (2-3 PM)
        {'teacher_id': 2, 'day_of_week': 'Monday', 'start_time': time(9, 0), 'end_time': time(10, 0)},
        {'teacher_id': 2, 'day_of_week': 'Tuesday', 'start_time': time(14, 0), 'end_time': time(15, 0)},
        
        # Teacher 3 - add Morning (9-10 AM) and Afternoon (2-3 PM) and Evening (9-10 PM)
        {'teacher_id': 3, 'day_of_week': 'Monday', 'start_time': time(9, 0), 'end_time': time(10, 0)},
        {'teacher_id': 3, 'day_of_week': 'Tuesday', 'start_time': time(14, 0), 'end_time': time(15, 0)},
        {'teacher_id': 3, 'day_of_week': 'Wednesday', 'start_time': time(21, 0), 'end_time': time(22, 0)},
    ]
    
    for slot_data in new_slots:
        slot = TimeSlot(**slot_data)
        db.add(slot)
    
    db.commit()
    print(f'✓ Added {len(new_slots)} time slots to existing teachers')
    print('\nTime slots now available:')
    print('Teacher 1 - Morning (9-10 AM), Afternoon (2-3 PM), Evening (9-10 PM)')
    print('Teacher 2 - Morning (9-10 AM), Afternoon (2-3 PM), Evening (5-6 PM)')
    print('Teacher 3 - Morning (9-10 AM), Afternoon (2-3 PM), Evening (9-10 PM)')
except Exception as e:
    print(f'Error: {e}')
    db.rollback()
finally:
    db.close()
