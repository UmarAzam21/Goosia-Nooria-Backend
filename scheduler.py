from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta, time as dt_time
from sqlalchemy.orm import Session
from sqlalchemy import cast, String
from database import SessionLocal
from models import Enrollment, Class, TimeSlot, ClassStatus, AttendanceStatus, EnrollmentStatus, PaymentStatus
import random
import string

def generate_meeting_id():
    """Generate a random meeting ID"""
    return ''.join(random.choices(string.digits, k=11))

def create_daily_classes():
    """Automatically create daily class entries for all active enrollments"""
    db = SessionLocal()
    try:
        # Get all active enrollments that are approved by teacher  
        enrollments = db.query(Enrollment).filter(
            Enrollment.is_active == True,
            cast(Enrollment.payment_status, String) == "completed",
            cast(Enrollment.enrollment_status, String) == "approved"
        ).all()
        
        for enrollment in enrollments:
            # Get the time slot
            time_slot = db.query(TimeSlot).filter(TimeSlot.id == enrollment.time_slot_id).first()
            if not time_slot:
                continue
            
            # Check if class for today already exists
            today = datetime.now().date()
            day_name = today.strftime("%A")
            
            # Only create class if today matches the time slot day
            if day_name.lower() == time_slot.day_of_week.lower():
                existing_class = db.query(Class).filter(
                    Class.enrollment_id == enrollment.id,
                    Class.class_date == today
                ).first()
                
                if not existing_class:
                    # Create new class
                    meeting_id = generate_meeting_id()
                    zoom_link = f"https://zoom.us/j/{meeting_id}"
                    
                    new_class = Class(
                        enrollment_id=enrollment.id,
                        class_date=today,
                        start_time=time_slot.start_time,
                        end_time=time_slot.end_time,
                        zoom_link=zoom_link,
                        meeting_id=meeting_id,
                        status=ClassStatus.SCHEDULED,
                        attendance_status=AttendanceStatus.PENDING
                    )
                    db.add(new_class)
        
        db.commit()
        print(f"Daily classes created at {datetime.now()}")
    
    except Exception as e:
        print(f"Error creating daily classes: {e}")
        db.rollback()
    finally:
        db.close()

def start_scheduler():
    """Start the background scheduler"""
    scheduler = BackgroundScheduler()
    
    # Run every day at midnight to create classes for the next day
    scheduler.add_job(create_daily_classes, 'cron', hour=0, minute=0)
    
    # Also run immediately on startup
    create_daily_classes()
    
    scheduler.start()
    print("Scheduler started successfully")
