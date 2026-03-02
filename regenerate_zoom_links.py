"""
Regenerate Zoom links using real Zoom API
Creates actual Zoom meetings instead of fake meeting IDs
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Enrollment
from database import engine
from datetime import datetime, time as dt_time
import os

# Try to use real Zoom API
try:
    from zoom_api_service import create_zoom_meeting_via_api, ZOOM_CLIENT_ID
    USE_ZOOM_API = bool(ZOOM_CLIENT_ID)
except ImportError:
    USE_ZOOM_API = False

# Fallback to simple zoom meeting generation
from zoom_service import create_zoom_meeting

# Create session
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Get all enrollments
    enrollments = db.query(Enrollment).all()
    
    print(f"\nRegenerating Zoom links for {len(enrollments)} enrollments...")
    
    if not USE_ZOOM_API:
        print("⚠️  Zoom API not configured - using fallback method")
        print("   For real Zoom meetings, configure ZOOM_CLIENT_ID and ZOOM_CLIENT_SECRET in .env")
        print("   See ZOOM_API_SETUP.md for instructions\n")
    else:
        print("✅ Zoom API configured - creating REAL Zoom meetings\n")
    
    for enrollment in enrollments:
        course_name = enrollment.course.name if enrollment.course else "Online Class"
        start_datetime = datetime.combine(enrollment.start_date, dt_time(9, 0))
        
        # Create Zoom meeting
        if USE_ZOOM_API:
            # Use real API
            zoom_result = create_zoom_meeting_via_api(
                event_name=f"{course_name} - {enrollment.student.name}",
                start_time=start_datetime,
                duration_minutes=60
            )
        else:
            # Use fallback
            zoom_result = create_zoom_meeting(
                event_name=course_name,
                start_time=start_datetime,
                end_time=start_datetime.replace(hour=start_datetime.hour + 1),
                description=f"Online class for {course_name}",
                event_id=str(enrollment.id)
            )
        
        if zoom_result["success"]:
            meeting_id = zoom_result.get("meeting_id", "N/A")
            zoom_link = zoom_result.get("zoom_link")
            
            # Update enrollment
            enrollment.zoom_link = zoom_link
            db.commit()
            
            print(f"✅ Enrollment {enrollment.id}: {meeting_id}")
            print(f"   Link: {zoom_link}\n")
        else:
            print(f"❌ Failed for enrollment {enrollment.id}: {zoom_result.get('error')}\n")

    print("✓ All enrollments regenerated!")
    print("\nNote: If using API method, real Zoom meetings were created.")
    print("Students can now join these meetings via the links.")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
