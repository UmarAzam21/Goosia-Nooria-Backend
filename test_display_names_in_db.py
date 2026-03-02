"""
Test the complete Jitsi integration with display names
Direct database testing to verify enrollment has display name in jitsi_link
"""

from database import SessionLocal
from models import Enrollment, User
from datetime import datetime

def test_display_names_in_database():
    """Check if enrollments have display names in their jitsi_links"""
    
    print("\n" + "="*70)
    print("  TESTING JITSI LINKS WITH DISPLAY NAMES IN DATABASE")
    print("="*70 + "\n")
    
    db = SessionLocal()
    
    try:
        # Get all enrollments
        enrollments = db.query(Enrollment).all()
        
        print(f"Total enrollments in database: {len(enrollments)}\n")
        
        if len(enrollments) == 0:
            print("⚠️  No enrollments found in database")
            return
        
        print("Enrollment Details:")
        print("-" * 70)
        
        for enrollment in enrollments:
            student = db.query(User).filter(User.id == enrollment.student_id).first()
            student_name = student.name if student else "Unknown"
            
            print(f"\n📋 Enrollment ID: {enrollment.id}")
            print(f"   Student: {student_name} (ID: {enrollment.student_id})")
            print(f"   Course ID: {enrollment.course_id}")
            print(f"   Status: {enrollment.enrollment_status}")
            print(f"   Payment Status: {enrollment.payment_status}")
            
            jitsi_link = enrollment.jitsi_link
            if jitsi_link:
                print(f"\n   Jitsi Link: {jitsi_link}")
                
                # Check if display name is included
                if "#userInfo.displayName=" in jitsi_link:
                    # Extract display name from URL
                    display_name_part = jitsi_link.split("#userInfo.displayName=")[1]
                    print(f"\n   ✅ DISPLAY NAME INCLUDED!")
                    print(f"      Display Name: {display_name_part}")
                    print(f"      Expected: {student_name}")
                    
                    # Check if display name matches student name
                    if display_name_part == student_name:
                        print(f"      ✅ Display name MATCHES student name!")
                    else:
                        print(f"      ⚠️  Display name doesn't match (this might be intentional)")
                else:
                    print(f"\n   ⚠️  No display name in Jitsi link")
                    print(f"      The link will not have the student's name pre-filled")
                    
                # Parse the base room URL
                if "#" in jitsi_link:
                    base_url = jitsi_link.split("#")[0]
                    print(f"\n   Base Room URL: {base_url}")
                    room_id = base_url.replace("https://meet.jitsi.net/", "")
                    print(f"   Room ID: {room_id}")
                else:
                    print(f"\n   Room URL: {jitsi_link}")
                    room_id = jitsi_link.replace("https://meet.jitsi.net/", "")
                    print(f"   Room ID: {room_id}")
            else:
                print(f"\n   ❌ No jitsi_link assigned!")
        
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        enrollments_with_display_names = sum(
            1 for e in enrollments 
            if e.jitsi_link and "#userInfo.displayName=" in e.jitsi_link
        )
        
        print(f"\nEnrollments with display names: {enrollments_with_display_names}/{len(enrollments)}")
        
        if enrollments_with_display_names == len(enrollments):
            print("✅ SUCCESS: All enrollments have display names in their Jitsi links!")
        elif enrollments_with_display_names > 0:
            print(f"⚠️  PARTIAL: {enrollments_with_display_names} out of {len(enrollments)} enrollments have display names")
        else:
            print("❌ FAILED: No enrollments have display names in their Jitsi links")
        
        print("\n" + "="*70)
        
        # Show example URLs for browser testing
        print("\nEXAMPLE JITSI URLs FOR BROWSER TESTING:")
        print("-" * 70)
        for enrollment in enrollments[:2]:  # Show first 2
            if enrollment.jitsi_link:
                print(f"\n📌 Enrollment {enrollment.id}:")
                print(f"   {enrollment.jitsi_link}")
        
        print("\n" + "="*70 + "\n")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_display_names_in_database()
