from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta, time

from database import get_db
from models import Enrollment, Course, Teacher, TimeSlot, Payment, User, PaymentStatus, UserRole, EnrollmentStatus, Notification, Class, ClassStatus, CourseGroup
from schemas import EnrollmentCreate, EnrollmentResponse
from auth import get_current_user

router = APIRouter()

@router.post("/", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
def create_enrollment(
    enrollment: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new enrollment"""
    # Check course limit for students (max 2 courses)
    if current_user.role == UserRole.STUDENT:
        active_enrollments = db.query(Enrollment).filter(
            Enrollment.student_id == current_user.id,
            Enrollment.is_active == True
        ).count()
        
        if active_enrollments >= 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Students can enroll in a maximum of 2 courses. You have already enrolled in 2 courses."
            )
    
    # Verify course exists
    course = db.query(Course).filter(Course.id == enrollment.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Verify teacher exists
    teacher = db.query(Teacher).filter(Teacher.id == enrollment.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    # Verify time slot exists and is available
    time_slot = db.query(TimeSlot).filter(
        TimeSlot.id == enrollment.time_slot_id,
        TimeSlot.teacher_id == enrollment.teacher_id
    ).first()
    if not time_slot:
        raise HTTPException(status_code=404, detail="Time slot not found")
    
    # Calculate end date based on course duration
    end_date = enrollment.start_date + timedelta(weeks=course.duration_weeks)
    
    # Generate unique Jitsi Meet room link
    # Room name format: course-teacher-student-enrollment (e.g., course1-ahmed-ali-12345)
    jitsi_room_name = f"noori-{course.id}-{teacher.id}-{current_user.id}-{int(datetime.now().timestamp())}"
    jitsi_meet_link = f"https://meet.jit.si/{jitsi_room_name}"
    
    # Create enrollment
    db_enrollment = Enrollment(
        student_id=current_user.id,
        course_id=enrollment.course_id,
        teacher_id=enrollment.teacher_id,
        time_slot_id=enrollment.time_slot_id,
        payment_method=enrollment.payment_method,
        start_date=enrollment.start_date,
        end_date=end_date,
        payment_status=PaymentStatus.PENDING if enrollment.payment_method == "at_masjid" else PaymentStatus.PENDING,
        zoom_link=jitsi_meet_link
    )
    db.add(db_enrollment)
    db.commit()
    db.refresh(db_enrollment)
    
    # Generate daily classes for the course duration (excluding Friday which is holiday)
    # Friday is weekday 4 (Monday=0, Friday=4)
    current_date = enrollment.start_date
    classes_created = 0
    
    while current_date <= end_date:
        # Skip Friday (weekday 4)
        if current_date.weekday() != 4:
            # Get the time slot times
            class_time_start = time(hour=time_slot.start_time.hour, minute=time_slot.start_time.minute)
            class_time_end = time(hour=time_slot.end_time.hour, minute=time_slot.end_time.minute)
            
            # Create class entry for this day
            class_obj = Class(
                enrollment_id=db_enrollment.id,
                class_date=current_date,
                start_time=class_time_start,
                end_time=class_time_end,
                zoom_link=jitsi_meet_link,
                status=ClassStatus.SCHEDULED
            )
            db.add(class_obj)
            classes_created += 1
        
        # Move to next day
        current_date += timedelta(days=1)
    
    db.commit()
    print(f"[INFO] Created {classes_created} daily classes for enrollment ID {db_enrollment.id}")
    
    # Create payment record
    payment = Payment(
        enrollment_id=db_enrollment.id,
        amount=course.fee,
        payment_method=enrollment.payment_method,
        payment_status=PaymentStatus.PENDING
    )
    db.add(payment)
    db.commit()
    
    # Auto-create course group for communication between student, teacher, and admin
    group_name = f"{course.name} - {teacher.user.name} & {current_user.name}"
    course_group = CourseGroup(
        course_id=course.id,
        enrollment_id=db_enrollment.id,
        group_name=group_name,
        is_active=True
    )
    db.add(course_group)
    db.commit()
    print(f"[INFO] Created course group: {group_name} for enrollment ID {db_enrollment.id}")
    
    return db_enrollment

@router.get("/my-enrollments", response_model=List[EnrollmentResponse])
def get_my_enrollments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all enrollments for the current user"""
    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id
    ).all()
    return enrollments

@router.get("/{enrollment_id}", response_model=EnrollmentResponse)
def get_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific enrollment"""
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    # Students can only view their own enrollments
    if current_user.role == UserRole.STUDENT and enrollment.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return enrollment

@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel an enrollment"""
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    # Only the student who enrolled or admin can cancel
    if current_user.role == UserRole.STUDENT and enrollment.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    enrollment.is_active = False
    db.commit()
    return None

@router.get("/teacher/pending-approvals")
def get_pending_enrollments_for_teacher(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get enrollments pending teacher approval"""
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="Teacher access only")
    
    teacher_profile = current_user.teacher_profile
    if not teacher_profile:
        raise HTTPException(status_code=404, detail="Teacher profile not found")
    
    # Get all pending enrollments regardless of payment status
    # Teacher can approve/reject before payment is completed
    enrollments = db.query(Enrollment).filter(
        Enrollment.teacher_id == teacher_profile.id,
        Enrollment.enrollment_status == EnrollmentStatus.PENDING_TEACHER,
        Enrollment.is_active == True
    ).all()
    print(f"[INFO] Retrieved {len(enrollments)} pending enrollments for teacher {current_user.email}")
    
    result = []
    for enrollment in enrollments:
        result.append({
            "enrollment_id": enrollment.id,
            "student_name": enrollment.student.name,
            "student_email": enrollment.student.email,
            "student_phone": enrollment.student.phone,
            "course_name": enrollment.course.name,
            "schedule": f"{enrollment.time_slot.day_of_week} at {enrollment.time_slot.start_time}",
            "start_date": enrollment.start_date,
            "duration_weeks": enrollment.course.duration_weeks,
            "created_at": enrollment.created_at
        })
    
    return result

@router.post("/{enrollment_id}/approve", response_model=EnrollmentResponse)
def approve_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve student enrollment (Teacher only)"""
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="Teacher access only")
    
    teacher_profile = current_user.teacher_profile
    if not teacher_profile:
        raise HTTPException(status_code=404, detail="Teacher profile not found")
    
    enrollment = db.query(Enrollment).filter(
        Enrollment.id == enrollment_id,
        Enrollment.teacher_id == teacher_profile.id
    ).first()
    
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    if enrollment.enrollment_status == EnrollmentStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Already approved")
    
    # Update enrollment status
    enrollment.enrollment_status = EnrollmentStatus.APPROVED
    
    # Notify student
    notification = Notification(
        user_id=enrollment.student_id,
        title="Enrollment Approved!",
        message=f"Your enrollment in '{enrollment.course.name}' with teacher '{current_user.name}' has been approved. You can now join classes at {enrollment.time_slot.day_of_week} {enrollment.time_slot.start_time}.",
        type="enrollment_approved"
    )
    db.add(notification)
    
    db.commit()
    db.refresh(enrollment)
    
    return enrollment

@router.post("/{enrollment_id}/reject", response_model=EnrollmentResponse)
def reject_enrollment(
    enrollment_id: int,
    reason: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reject student enrollment (Teacher only)"""
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="Teacher access only")
    
    teacher_profile = current_user.teacher_profile
    if not teacher_profile:
        raise HTTPException(status_code=404, detail="Teacher profile not found")
    
    enrollment = db.query(Enrollment).filter(
        Enrollment.id == enrollment_id,
        Enrollment.teacher_id == teacher_profile.id
    ).first()
    
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    # Update enrollment status
    enrollment.enrollment_status = EnrollmentStatus.REJECTED
    enrollment.is_active = False
    
    # Notify student
    rejection_message = f"Your enrollment in '{enrollment.course.name}' has been declined by the teacher."
    if reason:
        rejection_message += f" Reason: {reason}"
    
    notification = Notification(
        user_id=enrollment.student_id,
        title="Enrollment Declined",
        message=rejection_message,
        type="enrollment_rejected"
    )
    db.add(notification)
    
    db.commit()
    db.refresh(enrollment)
    
    return enrollment
