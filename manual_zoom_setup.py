#!/usr/bin/env python3
"""
WORKAROUND: Generate valid Zoom meeting IDs manually
Use this when Zoom API authentication isn't working

This allows you to:
1. Create meetings manually in Zoom
2. Add their real meeting IDs to the system
3. Students can join without "Invalid meeting ID" errors
"""

from database import SessionLocal
from models import Enrollment, Class
from datetime import datetime
import sys

def set_zoom_link_manually(enrollment_id: int, zoom_meeting_id: str):
    """
    Manually set a Zoom meeting ID for an enrollment
    
    Args:
        enrollment_id: ID of the enrollment
        zoom_meeting_id: Real Zoom meeting ID (e.g., 12345678901)
    """
    db = SessionLocal()
    
    try:
        enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
        
        if not enrollment:
            print(f"❌ Enrollment {enrollment_id} not found")
            return False
        
        # Format as proper Zoom link
        zoom_link = f"https://zoom.us/j/{zoom_meeting_id}"
        enrollment.zoom_link = zoom_link
        
        db.commit()
        print(f"✅ Enrollment {enrollment_id}:")
        print(f"   Zoom Link: {zoom_link}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def update_class_zoom_link(class_id: int, zoom_meeting_id: str):
    """
    Manually set a Zoom meeting ID for a class
    
    Args:
        class_id: ID of the class
        zoom_meeting_id: Real Zoom meeting ID (e.g., 12345678901)
    """
    db = SessionLocal()
    
    try:
        cls = db.query(Class).filter(Class.id == class_id).first()
        
        if not cls:
            print(f"❌ Class {class_id} not found")
            return False
        
        # Format as proper Zoom link
        zoom_link = f"https://zoom.us/j/{zoom_meeting_id}"
        cls.zoom_link = zoom_link
        
        db.commit()
        print(f"✅ Class {class_id}:")
        print(f"   Zoom Link: {zoom_link}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def list_all_enrollments():
    """Show all enrollments so you can match them with Zoom meeting IDs"""
    db = SessionLocal()
    
    try:
        enrollments = db.query(Enrollment).all()
        
        print("=" * 80)
        print("ALL ENROLLMENTS")
        print("=" * 80)
        
        for e in enrollments:
            print(f"\nID: {e.id}")
            print(f"  Status: {e.enrollment_status}")
            print(f"  Current Link: {e.zoom_link}")
            print(f"  Student ID: {e.student_id}")
        
        db.close()
        return enrollments
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.close()
        return []


def list_all_classes():
    """Show all classes so you can match them with Zoom meeting IDs"""
    db = SessionLocal()
    
    try:
        classes = db.query(Class).all()
        
        print("=" * 80)
        print("ALL CLASSES")
        print("=" * 80)
        
        for c in classes:
            print(f"\nID: {c.id}")
            print(f"  Name: {c.name}")
            print(f"  Current Link: {c.zoom_link}")
            print(f"  Teacher ID: {c.teacher_id}")
        
        db.close()
        return classes
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.close()
        return []


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║             ZOOM MANUAL MEETING ID CONFIGURATION TOOL                      ║
║                    (Use when API auth isn't working)                        ║
╚════════════════════════════════════════════════════════════════════════════╝

USAGE:

1. To see all enrollments:
   python manual_zoom_setup.py --list-enrollments

2. To see all classes:
   python manual_zoom_setup.py --list-classes

3. To set enrollment Zoom link:
   python manual_zoom_setup.py --set-enrollment <enrollment_id> <zoom_meeting_id>
   
   Example:
   python manual_zoom_setup.py --set-enrollment 1 12345678901

4. To set class Zoom link:
   python manual_zoom_setup.py --set-class <class_id> <zoom_meeting_id>
   
   Example:
   python manual_zoom_setup.py --set-class 1 98765432109

STEPS:

1. Create a meeting in Zoom (https://zoom.us)
2. Copy the meeting ID from Zoom
3. Use this tool to add it to your system
4. Students can now join!

────────────────────────────────────────────────────────────────────────────
    """)
    
    if len(sys.argv) < 2:
        print("ERROR: Missing command")
        print("\nExample:")
        print("  python manual_zoom_setup.py --list-enrollments")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "--list-enrollments":
        list_all_enrollments()
    
    elif command == "--list-classes":
        list_all_classes()
    
    elif command == "--set-enrollment":
        if len(sys.argv) != 4:
            print("ERROR: Missing arguments")
            print("Usage: python manual_zoom_setup.py --set-enrollment <enrollment_id> <zoom_meeting_id>")
            sys.exit(1)
        
        enrollment_id = int(sys.argv[2])
        zoom_id = sys.argv[3]
        set_zoom_link_manually(enrollment_id, zoom_id)
    
    elif command == "--set-class":
        if len(sys.argv) != 4:
            print("ERROR: Missing arguments")
            print("Usage: python manual_zoom_setup.py --set-class <class_id> <zoom_meeting_id>")
            sys.exit(1)
        
        class_id = int(sys.argv[2])
        zoom_id = sys.argv[3]
        update_class_zoom_link(class_id, zoom_id)
    
    else:
        print(f"ERROR: Unknown command '{command}'")
        print("\nValid commands:")
        print("  --list-enrollments")
        print("  --list-classes")
        print("  --set-enrollment <id> <meeting_id>")
        print("  --set-class <id> <meeting_id>")
        sys.exit(1)
