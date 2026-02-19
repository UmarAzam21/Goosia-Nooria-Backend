from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from models import (
    User, UserRole, StudentProfile, Enrollment, Certificate, 
    CourseGroup, GroupMessage
)
from schemas import (
    StudentProfileResponse, StudentProfileCreate, CertificateResponse,
    CourseGroupResponse, GroupMessageResponse
)
from auth import get_current_user, get_password_hash, verify_password
import uuid
import secrets

router = APIRouter()

@router.get("/profile", response_model=StudentProfileResponse)
def get_student_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get student profile"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this"
        )
    
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        # Create default profile if doesn't exist
        profile = StudentProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    return profile

@router.put("/profile", response_model=StudentProfileResponse)
def update_student_profile(
    profile_data: StudentProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update student profile"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this"
        )
    
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        profile = StudentProfile(user_id=current_user.id)
        db.add(profile)
    
    profile.bio = profile_data.bio
    profile.profile_picture_url = profile_data.profile_picture_url
    profile.preferred_language = profile_data.preferred_language
    profile.notify_via_email = profile_data.notify_via_email
    profile.notify_via_sms = profile_data.notify_via_sms
    
    db.commit()
    db.refresh(profile)
    print(f"[INFO] Student profile updated: {current_user.email}")
    return profile

@router.post("/password/change")
def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change password"""
    if not verify_password(current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    if len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters"
        )
    
    current_user.password_hash = get_password_hash(new_password)
    db.commit()
    print(f"[INFO] Password changed for user: {current_user.email}")
    return {"message": "Password changed successfully"}

@router.get("/enrollments", response_model=List[dict])
def get_enrollment_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get student enrollment history"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this"
        )
    
    enrollments = db.query(Enrollment).filter(Enrollment.student_id == current_user.id).all()
    
    result = []
    for enrollment in enrollments:
        enrollment_data = {
            "id": enrollment.id,
            "course_name": enrollment.course.name,
            "course_id": enrollment.course_id,
            "teacher_name": enrollment.teacher.user.name if enrollment.teacher else None,
            "start_date": enrollment.start_date,
            "end_date": enrollment.end_date,
            "status": enrollment.enrollment_status,
            "payment_status": enrollment.payment_status,
            "is_completed": datetime.now().date() > enrollment.end_date,
            "has_certificate": bool(enrollment.certificate)
        }
        result.append(enrollment_data)
    
    return result

@router.get("/enrollments/{enrollment_id}/performance")
def get_enrollment_performance(
    enrollment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get performance report for an enrollment"""
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )
    
    if enrollment.student_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this enrollment"
        )
    
    # Calculate performance metrics
    classes = db.query(__import__('models', fromlist=['Class']).Class).filter(
        __import__('models', fromlist=['Class']).Class.enrollment_id == enrollment_id
    ).all()
    
    attended = sum(1 for c in classes if c.attendance_status == "present")
    total = len(classes)
    attendance_rate = (attended / total * 100) if total > 0 else 0
    
    return {
        "enrollment_id": enrollment_id,
        "course_name": enrollment.course.name,
        "total_classes": total,
        "attended_classes": attended,
        "attendance_rate": round(attendance_rate, 2),
        "status": enrollment.enrollment_status,
        "start_date": enrollment.start_date,
        "end_date": enrollment.end_date,
        "days_remaining": (enrollment.end_date - datetime.now().date()).days
    }

@router.get("/certificates/{enrollment_id}", response_model=CertificateResponse)
def get_certificate(
    enrollment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get certificate for completed course"""
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )
    
    if enrollment.student_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this certificate"
        )
    
    certificate = db.query(Certificate).filter(Certificate.enrollment_id == enrollment_id).first()
    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not issued yet"
        )
    
    return certificate

@router.post("/certificates/{enrollment_id}/generate")
def generate_certificate(
    enrollment_id: int,
    completion_percentage: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate certificate for completed course (Admin/Teacher)"""
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )
    
    if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin/teacher can generate certificates"
        )
    
    if completion_percentage < 75:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student must complete at least 75% of course"
        )
    
    # Check if certificate already exists
    existing = db.query(Certificate).filter(Certificate.enrollment_id == enrollment_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Certificate already issued"
        )
    
    # Generate certificate
    certificate_number = f"CERT-{datetime.now().year}-{secrets.token_hex(6).upper()}"
    certificate = Certificate(
        enrollment_id=enrollment_id,
        student_id=enrollment.student_id,
        course_id=enrollment.course_id,
        certificate_number=certificate_number,
        issued_date=datetime.now().date(),
        completion_percentage=completion_percentage
    )
    
    db.add(certificate)
    db.commit()
    db.refresh(certificate)
    print(f"[INFO] Certificate issued: {certificate_number} for student {enrollment.student.email}")
    
    return certificate

