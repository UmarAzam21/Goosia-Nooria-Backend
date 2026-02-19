from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User, UserRole, Course, Teacher, Enrollment, Payment, PaymentStatus
from schemas import UserResponse, CourseResponse, CourseCreate
from auth import require_admin, get_current_user

router = APIRouter()

# ==================== COURSE MANAGEMENT ====================

@router.get("/courses", response_model=List[CourseResponse])
def get_all_courses(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Get all courses"""
    courses = db.query(Course).all()
    return courses

@router.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    course: CourseCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Create a new course"""
    try:
        db_course = Course(
            name=course.name,
            description=course.description,
            duration_weeks=course.duration_weeks,
            fee=course.fee,
            currency=course.currency
        )
        db.add(db_course)
        db.commit()
        db.refresh(db_course)
        print(f"[INFO] Course created: {db_course.name} (ID: {db_course.id}) by admin {admin.email}")
        return db_course
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating course: {str(e)}"
        )

@router.put("/courses/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int,
    course: CourseCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Update course details (name, description, price, duration)"""
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    try:
        db_course.name = course.name
        db_course.description = course.description
        db_course.duration_weeks = course.duration_weeks
        db_course.fee = course.fee
        db_course.currency = course.currency
        
        db.commit()
        db.refresh(db_course)
        print(f"[INFO] Course updated: {db_course.name} (ID: {db_course.id}) by admin {admin.email}")
        return db_course
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating course: {str(e)}"
        )

@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Delete a course"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Delete enrollments associated with this course
    db.query(Enrollment).filter(Enrollment.course_id == course_id).delete()
    
    # Delete the course
    db.delete(course)
    db.commit()
    
    return None

@router.put("/courses/{course_id}/activate")
def activate_course(
    course_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Activate a course"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    course.is_active = True
    db.commit()
    db.refresh(course)
    return course

@router.put("/courses/{course_id}/deactivate")
def deactivate_course(
    course_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Deactivate a course"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    course.is_active = False
    db.commit()
    db.refresh(course)
    return course

# ==================== TEACHER MANAGEMENT ====================

@router.get("/teachers", response_model=List[UserResponse])
def get_all_teachers(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Get all teachers"""
    teachers = db.query(User).filter(User.role == UserRole.TEACHER).all()
    return teachers

@router.put("/teachers/{teacher_id}/freeze")
def freeze_teacher(
    teacher_id: int,
    reason: str = "Unapproved content",
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Freeze a teacher account (soft delete)"""
    teacher = db.query(User).filter(User.id == teacher_id, User.role == UserRole.TEACHER).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )
    
    teacher.frozen_by_admin = True
    teacher.freeze_reason = reason
    db.commit()
    db.refresh(teacher)
    
    return {
        "message": "Teacher account frozen by admin",
        "user_id": teacher.id,
        "status": "frozen_by_admin",
        "reason": reason
    }

@router.put("/teachers/{teacher_id}/unfreeze")
def unfreeze_teacher(
    teacher_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Unfreeze a teacher account"""
    teacher = db.query(User).filter(User.id == teacher_id, User.role == UserRole.TEACHER).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )
    
    teacher.frozen_by_admin = False
    teacher.freeze_reason = None
    db.commit()
    db.refresh(teacher)
    
    return {
        "message": "Teacher account unfrozen",
        "user_id": teacher.id,
        "status": "active"
    }

# ==================== STUDENT MANAGEMENT ====================

@router.get("/students", response_model=List[UserResponse])
def get_all_students(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Get all students"""
    students = db.query(User).filter(User.role == UserRole.STUDENT).all()
    return students

@router.put("/students/{student_id}/freeze")
def freeze_student(
    student_id: int,
    reason: str = "Policy violation",
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Freeze a student account (soft delete)"""
    student = db.query(User).filter(User.id == student_id, User.role == UserRole.STUDENT).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    student.frozen_by_admin = True
    student.freeze_reason = reason
    db.commit()
    db.refresh(student)
    
    return {
        "message": "Student account frozen by admin",
        "user_id": student.id,
        "status": "frozen_by_admin",
        "reason": reason
    }

@router.put("/students/{student_id}/unfreeze")
def unfreeze_student(
    student_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Unfreeze a student account"""
    student = db.query(User).filter(User.id == student_id, User.role == UserRole.STUDENT).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    student.frozen_by_admin = False
    student.freeze_reason = None
    db.commit()
    db.refresh(student)
    
    return {
        "message": "Student account unfrozen",
        "user_id": student.id,
        "status": "active"
    }

# ==================== PAYMENT MANAGEMENT ====================

@router.get("/payments")
def get_all_payments(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Get all payments"""
    payments = db.query(Payment).all()
    return [
        {
            "id": p.id,
            "enrollment_id": p.enrollment_id,
            "amount": p.amount,
            "payment_method": p.payment_method,
            "payment_status": p.payment_status,
            "transaction_id": p.transaction_id,
            "paid_at": p.paid_at,
            "created_at": p.created_at
        }
        for p in payments
    ]

@router.put("/payments/{payment_id}/approve")
def approve_payment(
    payment_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Approve a payment"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    payment.payment_status = PaymentStatus.COMPLETED
    db.commit()
    db.refresh(payment)
    
    return {
        "message": "Payment approved",
        "payment_id": payment.id,
        "status": "completed"
    }

@router.put("/payments/{payment_id}/reject")
def reject_payment(
    payment_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Reject a payment"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    payment.payment_status = PaymentStatus.FAILED
    db.commit()
    db.refresh(payment)
    
    return {
        "message": "Payment rejected",
        "payment_id": payment.id,
        "status": "failed"
    }

# ==================== USER MANAGEMENT ====================

@router.get("/users")
def get_all_users(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Get all users"""
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role.value if hasattr(u.role, 'value') else str(u.role),
            "phone": u.phone,
            "frozen_by_admin": u.frozen_by_admin,
            "freeze_reason": u.freeze_reason,
            "created_at": u.created_at
        }
        for u in users
    ]

@router.get("/users/frozen")
def get_frozen_users(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Get all frozen users"""
    frozen_users = db.query(User).filter(User.frozen_by_admin == True).all()
    return [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role.value if hasattr(u.role, 'value') else str(u.role),
            "frozen_by_admin": u.frozen_by_admin,
            "freeze_reason": u.freeze_reason,
            "created_at": u.created_at
        }
        for u in frozen_users
    ]

# ==================== DASHBOARD STATS ====================

@router.get("/stats")
def get_admin_stats(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Get system statistics"""
    total_users = db.query(User).count()
    total_students = db.query(User).filter(User.role == UserRole.STUDENT).count()
    total_teachers = db.query(User).filter(User.role == UserRole.TEACHER).count()
    frozen_users = db.query(User).filter(User.frozen_by_admin == True).count()
    total_courses = db.query(Course).count()
    total_enrollments = db.query(Enrollment).count()
    total_payments = db.query(Payment).count()
    completed_payments = db.query(Payment).filter(Payment.payment_status == PaymentStatus.COMPLETED).count()
    
    return {
        "total_users": total_users,
        "total_students": total_students,
        "total_teachers": total_teachers,
        "frozen_users": frozen_users,
        "total_courses": total_courses,
        "active_courses": db.query(Course).filter(Course.is_active == True).count(),
        "total_enrollments": total_enrollments,
        "total_payments": total_payments,
        "completed_payments": completed_payments,
        "pending_payments": db.query(Payment).filter(Payment.payment_status == PaymentStatus.PENDING).count()
    }
