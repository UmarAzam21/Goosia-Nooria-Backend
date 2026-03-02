"""
Update existing enrollments with Zoom links
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Enrollment
from database import get_db, engine
from zoom_service import create_zoom_meeting
from datetime import datetime, timedelta, time as dt_time

# Connect to database
with engine.connect() as conn:
    result = conn.execute(text("SELECT id FROM enrollments WHERE zoom_link IS NULL OR zoom_link = '' LIMIT 10"))
    enrollment_ids = [row[0] for row in result]
    conn.commit()

print(f"Found {len(enrollment_ids)} enrollments without zoom links")

# Create new session
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    for enrollment_id in enrollment_ids:
        enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
        
        if not enrollment:
            print(f"❌ Enrollment {enrollment_id} not found")
            continue
        
        # Generate Zoom link if doesn't exist
        if not enrollment.zoom_link:
            course_name = enrollment.course.name if enrollment.course else "Online Class"
            
            # Create Zoom meeting
            zoom_result = create_zoom_meeting(
                event_name=course_name,
                start_time=datetime.combine(enrollment.start_date, dt_time(9, 0)),
                end_time=datetime.combine(enrollment.start_date, dt_time(10, 0)),
                description=f"Online class for {course_name}",
                event_id=str(enrollment.id)
            )
            
            if zoom_result["success"]:
                enrollment.zoom_link = zoom_result.get("zoom_link")
                db.commit()
                print(f"✅ Updated enrollment {enrollment_id}: {enrollment.zoom_link}")
            else:
                print(f"❌ Failed to create Zoom meeting for enrollment {enrollment_id}")
        else:
            print(f"⚠️  Enrollment {enrollment_id} already has zoom_link: {enrollment.zoom_link}")

    print("\n✓ All existing enrollments updated!")

except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
