from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Course, User, UserRole, Enrollment, Teacher
from schemas import CourseCreate, CourseResponse
from auth import get_current_user, require_role

router = APIRouter()

@router.get("/", response_model=List[CourseResponse])
def get_all_courses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all active courses"""
    courses = db.query(Course).filter(Course.is_active == True).offset(skip).limit(limit).all()
    return courses

@router.get("/student/enrollment-limit")
def get_student_enrollment_limit(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get student's course enrollment limit status"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can check enrollment limits"
        )
    
    active_enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.is_active == True
    ).count()
    
    can_enroll = active_enrollments < 2
    remaining_slots = 2 - active_enrollments
    
    return {
        "active_enrollments": active_enrollments,
        "max_courses": 2,
        "remaining_slots": remaining_slots,
        "can_enroll_more": can_enroll,
        "message": f"You have enrolled in {active_enrollments}/2 courses. {'You can enroll in ' + str(remaining_slots) + ' more course(s).' if can_enroll else 'You have reached the maximum course limit.'}"
    }

@router.get("/my-courses/teacher")
def get_teacher_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all enrollments where the current teacher is assigned (with time slot details)"""
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can access their courses"
        )
    
    # Get teacher profile
    teacher_profile = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
    if not teacher_profile:
        # No teacher profile, return empty list
        return []
    
    # Get all enrollments where this teacher is assigned
    from sqlalchemy.orm import joinedload
    enrollments = db.query(Enrollment).filter(
        Enrollment.teacher_id == teacher_profile.id,
        Enrollment.is_active == True
    ).options(
        joinedload(Enrollment.course),
        joinedload(Enrollment.time_slot),
        joinedload(Enrollment.teacher)
    ).all()
    
    # Format response matching student enrollments
    result = []
    for enrollment in enrollments:
        teacher_name = "N/A"
        if enrollment.teacher and enrollment.teacher.user:
            teacher_name = enrollment.teacher.user.name or enrollment.teacher.user.email
        
        enrollment_data = {
            "id": enrollment.id,
            "course": {
                "id": enrollment.course.id,
                "name": enrollment.course.name,
                "fee": enrollment.course.fee,
                "description": enrollment.course.description,
                "duration_weeks": enrollment.course.duration_weeks,
                "currency": enrollment.course.currency
            },
            "teacher": {
                "id": enrollment.teacher.id,
                "name": teacher_name
            },
            "time_slot": {
                "day": enrollment.time_slot.day_of_week,
                "start_time": str(enrollment.time_slot.start_time),
                "end_time": str(enrollment.time_slot.end_time)
            } if enrollment.time_slot else None,
            "enrollment_status": enrollment.enrollment_status,
            "payment_status": enrollment.payment_status,
            "is_active": enrollment.is_active,
            "zoom_link": enrollment.zoom_link
        }
        result.append(enrollment_data)
    
    return result

@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    """Get a specific course by ID"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Create a new course (Admin only)"""
    db_course = Course(**course.dict())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int,
    course: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Update a course (Admin only)"""
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    for key, value in course.dict().items():
        setattr(db_course, key, value)
    
    db.commit()
    db.refresh(db_course)
    return db_course

@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Delete a course (Admin only)"""
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    db_course.is_active = False
    db.commit()
    return None
