from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from database import get_db
from models import (
    User, Course, Enrollment, Class, Payment, Teacher,
    UserRole, PaymentStatus, ClassStatus, Notification, EnrollmentStatus
)
from schemas import StudentDashboard, TeacherDashboard, AdminDashboard
from auth import get_current_user
from routers.classes import get_my_classes
from routers.enrollments import get_my_enrollments

router = APIRouter()

@router.get("/student", response_model=StudentDashboard)
def get_student_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get student dashboard data"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Student access only")
    
    # Get enrollments
    enrollments = get_my_enrollments(db=db, current_user=current_user)
    
    # Get today's classes
    today_classes = get_my_classes(date_filter="today", db=db, current_user=current_user)
    
    # Get upcoming classes
    upcoming_classes = get_my_classes(date_filter="upcoming", db=db, current_user=current_user)
    
    return StudentDashboard(
        enrollments=enrollments,
        today_classes=today_classes,
        upcoming_classes=upcoming_classes
    )

@router.get("/teacher")
def get_teacher_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get teacher dashboard data"""
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="Teacher access only")
    
    teacher_profile = current_user.teacher_profile
    
    # If teacher profile doesn't exist, create one
    if not teacher_profile:
        print(f"[INFO] Creating missing teacher profile for user: {current_user.email} (ID: {current_user.id})")
        teacher_profile = Teacher(
            user_id=current_user.id,
            bio="",
            experience_years=0,
            qualification="",
            is_available=True
        )
        db.add(teacher_profile)
        db.commit()
        db.refresh(teacher_profile)
    
    # Get today's and upcoming classes from actual Class records
    today_classes = get_my_classes(date_filter="today", db=db, current_user=current_user)
    upcoming_classes = get_my_classes(date_filter="upcoming", db=db, current_user=current_user)
    
    # If no classes found in Class table, get from enrollments (simpler approach)
    if not today_classes and not upcoming_classes:
        # Get teacher's approved enrollments (they can see these classes with zoom links)
        today = datetime.now().date()
        enrollments = db.query(Enrollment).filter(
            Enrollment.teacher_id == teacher_profile.id,
            Enrollment.enrollment_status == EnrollmentStatus.APPROVED,
            Enrollment.start_date <= today,
            Enrollment.end_date >= today
        ).all()
        
        # Convert to simple list format for frontend
        today_classes = []
        upcoming_classes = []
        for enrollment in enrollments:
            class_info = {
                "id": enrollment.id,
                "course_name": enrollment.course.name,
                "student_name": enrollment.student.name,
                "start_time": str(enrollment.time_slot.start_time),
                "end_time": str(enrollment.time_slot.end_time),
                "class_date": enrollment.start_date,
                "status": "scheduled",
                "attendance_status": "pending",
                "zoom_link": enrollment.zoom_link
            }
            today_classes.append(class_info)
        
        # Get upcoming enrollments
        future_enrollments = db.query(Enrollment).filter(
            Enrollment.teacher_id == teacher_profile.id,
            Enrollment.enrollment_status == EnrollmentStatus.APPROVED,
            Enrollment.start_date > today
        ).limit(10).all()
        
        for enrollment in future_enrollments:
            class_info = {
                "id": enrollment.id,
                "course_name": enrollment.course.name,
                "student_name": enrollment.student.name,
                "start_time": str(enrollment.time_slot.start_time),
                "end_time": str(enrollment.time_slot.end_time),
                "class_date": enrollment.start_date,
                "status": "scheduled",
                "attendance_status": "pending",
                "zoom_link": enrollment.zoom_link
            }
            upcoming_classes.append(class_info)
    
    # Get total students
    total_students = db.query(Enrollment).filter(
        Enrollment.teacher_id == teacher_profile.id,
        Enrollment.is_active == True
    ).count()
    
    return {
        "today_classes": today_classes,
        "upcoming_classes": upcoming_classes,
        "total_students": total_students
    }

@router.get("/admin", response_model=AdminDashboard)
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get admin dashboard data"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access only")
    
    # Total students
    total_students = db.query(User).filter(User.role == UserRole.STUDENT).count()
    
    # Total teachers
    total_teachers = db.query(Teacher).count()
    
    # Total courses
    total_courses = db.query(Course).filter(Course.is_active == True).count()
    
    # Total enrollments
    total_enrollments = db.query(Enrollment).filter(Enrollment.is_active == True).count()
    
    # Pending payments
    pending_payments = db.query(Payment).filter(
        Payment.payment_status == PaymentStatus.PENDING
    ).count()
    
    # Today's classes
    today = datetime.now().date()
    today_classes = db.query(Class).filter(Class.class_date == today).count()
    
    return AdminDashboard(
        total_students=total_students,
        total_teachers=total_teachers,
        total_courses=total_courses,
        total_enrollments=total_enrollments,
        pending_payments=pending_payments,
        today_classes=today_classes
    )

@router.get("/stats")
def get_overall_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get overall statistics (available to all authenticated users)"""
    total_courses = db.query(Course).filter(Course.is_active == True).count()
    total_teachers = db.query(Teacher).filter(Teacher.is_available == True).count()
    
    return {
        "total_courses": total_courses,
        "total_teachers": total_teachers,
        "message": "Welcome to Masjid Online Class Portal"
    }

@router.get("/admin/pending-enrollments")
def get_pending_enrollments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all enrollments with pending payments (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access only")
    
    enrollments = db.query(Enrollment).filter(
        Enrollment.payment_status == PaymentStatus.PENDING
    ).all()
    
    result = []
    for enrollment in enrollments:
        payment = db.query(Payment).filter(Payment.enrollment_id == enrollment.id).first()
        result.append({
            "enrollment_id": enrollment.id,
            "student_name": enrollment.student.name,
            "student_email": enrollment.student.email,
            "course_name": enrollment.course.name,
            "teacher_name": enrollment.teacher.user.name,
            "amount": enrollment.course.fee,
            "payment_method": payment.payment_method if payment else None,
            "transaction_id": payment.transaction_id if payment else None,
            "payment_proof_url": payment.payment_proof_url if payment else None,
            "payment_id": payment.id if payment else None,
            "created_at": enrollment.created_at
        })
    
    return result

@router.get("/admin/all-students")
def get_all_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all students (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access only")
    
    students = db.query(User).filter(User.role == UserRole.STUDENT).all()
    
    result = []
    for student in students:
        enrollments_count = db.query(Enrollment).filter(
            Enrollment.student_id == student.id,
            Enrollment.is_active == True
        ).count()
        
        result.append({
            "id": student.id,
            "name": student.name,
            "email": student.email,
            "phone": student.phone,
            "enrollments_count": enrollments_count,
            "created_at": student.created_at
        })
    
    return result

@router.get("/admin/all-teachers")
def get_all_teachers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all teachers (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access only")
    
    teachers = db.query(Teacher).all()
    
    result = []
    for teacher in teachers:
        students_count = db.query(Enrollment).filter(
            Enrollment.teacher_id == teacher.id,
            Enrollment.is_active == True
        ).count()
        
        result.append({
            "id": teacher.id,
            "name": teacher.user.name,
            "email": teacher.user.email,
            "phone": teacher.user.phone,
            "bio": teacher.bio,
            "experience_years": teacher.experience_years,
            "qualification": teacher.qualification,
            "students_count": students_count,
            "is_available": teacher.is_available
        })
    
    return result

@router.get("/notifications")
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get notifications for current user"""
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).limit(50).all()
    
    return notifications

@router.post("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark notification as read"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    db.commit()
    
    return {"message": "Notification marked as read"}

@router.get("/notifications/unread-count")
def get_unread_notifications_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get count of unread notifications"""
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    
    return {"unread_count": count}
