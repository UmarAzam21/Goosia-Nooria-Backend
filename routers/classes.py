from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date, timedelta

from database import get_db
from models import Class, Enrollment, User, UserRole, AttendanceStatus, ClassStatus, Notification, Teacher
from schemas import ClassCreate, ClassResponse, ClassWithDetails
from auth import get_current_user, require_role

router = APIRouter()

@router.get("/my-classes", response_model=List[ClassWithDetails])
def get_my_classes(
    date_filter: str = "today",  # today, upcoming, all
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get classes for the current user (student or teacher)"""
    today = datetime.now().date()
    
    if current_user.role == UserRole.STUDENT:
        # Get student's enrollments
        enrollments = db.query(Enrollment).filter(
            Enrollment.student_id == current_user.id,
            Enrollment.is_active == True
        ).all()
        enrollment_ids = [e.id for e in enrollments]
        
        query = db.query(Class).filter(Class.enrollment_id.in_(enrollment_ids))
    
    elif current_user.role == UserRole.TEACHER:
        # Get teacher's enrollments
        teacher_profile = current_user.teacher_profile
        if not teacher_profile:
            return []
        
        enrollments = db.query(Enrollment).filter(
            Enrollment.teacher_id == teacher_profile.id,
            Enrollment.is_active == True
        ).all()
        enrollment_ids = [e.id for e in enrollments]
        
        query = db.query(Class).filter(Class.enrollment_id.in_(enrollment_ids))
    
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Apply date filter
    if date_filter == "today":
        query = query.filter(Class.class_date == today)
    elif date_filter == "upcoming":
        query = query.filter(Class.class_date >= today)
    
    classes = query.order_by(Class.class_date, Class.start_time).all()
    
    # Enrich with details
    result = []
    for cls in classes:
        enrollment = db.query(Enrollment).filter(Enrollment.id == cls.enrollment_id).first()
        if enrollment:
            student = db.query(User).filter(User.id == enrollment.student_id).first()
            teacher_profile = db.query(User).join(User.teacher_profile).filter(
                User.teacher_profile.has(id=enrollment.teacher_id)
            ).first()
            
            class_dict = {
                **cls.__dict__,
                "student_name": student.name if student else "Unknown",
                "teacher_name": teacher_profile.name if teacher_profile else "Unknown",
                "course_name": enrollment.course.name if enrollment.course else "Unknown",
                "zoom_link": enrollment.zoom_link
            }
            result.append(ClassWithDetails(**class_dict))
    
    return result

@router.get("/{class_id}", response_model=ClassResponse)
def get_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific class"""
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Verify user has access to this class
    enrollment = db.query(Enrollment).filter(Enrollment.id == class_obj.enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    if current_user.role == UserRole.STUDENT and enrollment.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if current_user.role == UserRole.TEACHER:
        if not current_user.teacher_profile or enrollment.teacher_id != current_user.teacher_profile.id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return class_obj

@router.post("/{class_id}/join")
def join_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark attendance and get join link, send notifications to teacher/students and admin"""
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Allow class joining with very flexible timing (anytime on any day for demo)
    # In production, use: datetime.combine(class_obj.class_date, class_obj.start_time)
    # For testing: allow joining anytime
    # now = datetime.now()
    # class_datetime = datetime.combine(class_obj.class_date, class_obj.start_time)
    # join_window_start = class_datetime - timedelta(days=1)
    # class_end = class_datetime + timedelta(days=1)
    # 
    # if not (join_window_start <= now <= class_end):
    #     print(f"[DEBUG] Join window check failed. Now: {now}, Window: {join_window_start} to {class_end}")
    #     raise HTTPException(
    #         status_code=400,
    #         detail="Class can only be joined 1 hour before to 2 hours after start time"
    #     )
    
    # Get enrollment details
    enrollment = db.query(Enrollment).filter(Enrollment.id == class_obj.enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    print(f"[DEBUG] User {current_user.name} (ID: {current_user.id}, Role: {current_user.role}) joining class {class_id}")
    
    # Get student and teacher info
    student = db.query(User).filter(User.id == enrollment.student_id).first()
    
    # Get teacher user from the enrollment's teacher_id
    teacher_profile = db.query(Teacher).filter(Teacher.id == enrollment.teacher_id).first()
    teacher_user = None
    if teacher_profile:
        teacher_user = db.query(User).filter(User.id == teacher_profile.user_id).first()
    
    print(f"[DEBUG] Student: {student.name if student else 'None'}, Teacher: {teacher_user.name if teacher_user else 'None'}")
    
    # Get admin users
    admin_users = db.query(User).filter(User.role == UserRole.ADMIN).all()
    print(f"[DEBUG] Found {len(admin_users)} admins")
    
    # Mark attendance as present
    class_obj.attendance_status = AttendanceStatus.PRESENT
    class_obj.status = ClassStatus.IN_PROGRESS
    db.commit()
    
    # Send notifications
    notifications_created = 0
    
    if current_user.role == UserRole.STUDENT:
        # Student joined - notify teacher
        if teacher_user:
            teacher_notification = Notification(
                user_id=teacher_user.id,
                title="Student Joined Class",
                message=f"Student {student.name} has joined the {enrollment.course.name} class",
                type="student_joined"
            )
            db.add(teacher_notification)
            notifications_created += 1
            print(f"[DEBUG] Created notification for teacher {teacher_user.name}")
    
    elif current_user.role == UserRole.TEACHER:
        # Teacher joined - notify student
        if student:
            student_notification = Notification(
                user_id=student.id,
                title="Teacher Joined Class",
                message=f"Your teacher has joined the {enrollment.course.name} class",
                type="teacher_joined"
            )
            db.add(student_notification)
            notifications_created += 1
            print(f"[DEBUG] Created notification for student {student.name}")
    
    # Notify all admins
    for admin in admin_users:
        joiner_name = current_user.name
        joiner_role = "Student" if current_user.role == UserRole.STUDENT else "Teacher"
        admin_notification = Notification(
            user_id=admin.id,
            title=f"{joiner_role} Joined Class",
            message=f"{joiner_name} ({joiner_role}) has joined the {enrollment.course.name} class",
            type="class_join_admin"
        )
        db.add(admin_notification)
        notifications_created += 1
        print(f"[DEBUG] Created notification for admin {admin.name}")
    
    db.commit()
    print(f"[DEBUG] Total notifications created: {notifications_created}")
    
    # Extract room ID from jitsi_link for clarity
    room_id = class_obj.meeting_id or getattr(class_obj, 'meeting_id', 'unknown')
    
    # Ensure jitsi_link is a valid Jitsi URL
    jitsi_link = class_obj.jitsi_link
    if jitsi_link and not jitsi_link.startswith('https://'):
        jitsi_link = f"https://meet.jitsi.net/{jitsi_link}"
    
    return {
        "success": True,
        "jitsi_link": jitsi_link,  # Full URL: https://meet.jitsi.net/noorib9e224cc42
        "meeting_id": room_id,  # Just the room ID: noorib9e224cc42
        "jitsi_room": room_id,  # Same as meeting_id for clarity
        "jitsi_url": jitsi_link,  # Explicit Jitsi URL
        "class_name": enrollment.course.name if enrollment.course else "Class",
        "attendance_status": "present",
        "notifications_created": notifications_created,
        "message": f"Join the meeting at: {jitsi_link}",
        "instructions": "Click the zoom_link or jitsi_url to join the meeting directly"
    }

@router.put("/{class_id}/attendance")
def update_attendance(
    class_id: int,
    attendance_status: AttendanceStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.TEACHER, UserRole.ADMIN]))
):
    """Update class attendance (Teacher/Admin only)"""
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    class_obj.attendance_status = attendance_status
    db.commit()
    db.refresh(class_obj)
    
    return {"message": "Attendance updated successfully", "attendance_status": attendance_status}

@router.put("/{class_id}/upload")
def upload_class_materials(
    class_id: int,
    recorded_lecture_url: str = None,
    notes_url: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload class materials (Teacher only)"""
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="Only teachers can upload materials")
    
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Verify teacher owns this class
    enrollment = db.query(Enrollment).filter(Enrollment.id == class_obj.enrollment_id).first()
    if not enrollment or enrollment.teacher_id != current_user.teacher_profile.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if recorded_lecture_url:
        class_obj.recorded_lecture_url = recorded_lecture_url
    if notes_url:
        class_obj.notes_url = notes_url
    
    class_obj.status = ClassStatus.COMPLETED
    db.commit()
    
    return {"message": "Materials uploaded successfully"}

@router.get("/{class_id}/bbb-join-url")
def get_bbb_join_url(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get Google Meet calendar link for a class"""
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Verify user has access to this class
    enrollment = db.query(Enrollment).filter(Enrollment.id == class_obj.enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    # Check access permissions
    is_teacher = current_user.role == UserRole.TEACHER and current_user.teacher_profile and enrollment.teacher_id == current_user.teacher_profile.id
    is_student = current_user.role == UserRole.STUDENT and enrollment.student_id == current_user.id
    is_admin = current_user.role == UserRole.ADMIN
    
    if not (is_teacher or is_student or is_admin):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Return the Google Calendar/Meet link from enrollment
    if not enrollment.zoom_link:
        raise HTTPException(status_code=404, detail="Calendar link not found for this class")
    
    return {
        "meet_link": enrollment.zoom_link,
        "calendar_link": enrollment.zoom_link,
        "class_name": enrollment.course.name if enrollment.course else "Class",
        "is_organizer": is_teacher,
        "message": "Google Calendar with Meet link"
    }


@router.get("/{class_id}/open-meeting")
def open_class_meeting(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Redirect to Jitsi meeting room for the class
    This endpoint ensures students go DIRECTLY to the meeting, not to Jitsi homepage
    """
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Get enrollment to check access
    enrollment = db.query(Enrollment).filter(Enrollment.id == class_obj.enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    # Check if user is student or teacher
    is_student = current_user.id == enrollment.student_id
    is_teacher = current_user.id == enrollment.teacher.user_id if enrollment.teacher else False
    
    if not (is_student or is_teacher):
        raise HTTPException(status_code=403, detail="Access denied to this class")
    
    # Get the meeting link
    if not class_obj.zoom_link:
        raise HTTPException(status_code=404, detail="Meeting link not found for this class")
    
    # Mark attendance
    class_obj.attendance_status = AttendanceStatus.PRESENT
    class_obj.status = ClassStatus.IN_PROGRESS
    db.commit()
    
    # Return direct link to Jitsi room
    return {
        "meeting_url": class_obj.zoom_link,
        "room_id": class_obj.meeting_id,
        "class_name": enrollment.course.name if enrollment.course else "Class",
        "message": "Click the meeting_url link OR visit this address in your Jitsi app"
    }
