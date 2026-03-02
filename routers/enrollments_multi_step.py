from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import os
from datetime import datetime
from pathlib import Path
import uuid

from database import get_db
from models import (
    Enrollment, PaymentProof, Payment, User, Course, Teacher,
    TimeSlot, Notification, CourseGroup, StudentCourseGroup
)
from schemas import QuickEnrollRequest, EnrollmentResponse, PaymentProofResponse
from auth import get_current_user
from notification_service import NotificationService
from zoom_integration import create_zoom_meeting

router = APIRouter(prefix="/api/enrollments", tags=["enrollments"])

# Create upload directory for payment proofs
UPLOAD_DIR = Path("uploads/payment_proofs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/quick-enroll")
async def quick_enroll_course(
    request: QuickEnrollRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Quick enroll with auto-assign teacher and time slot"""
    try:
        # Verify course exists
        course = db.query(Course).filter(Course.id == request.course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Check if already enrolled
        existing = db.query(Enrollment).filter(
            and_(
                Enrollment.student_id == current_user["id"],
                Enrollment.course_id == request.course_id
            )
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Already enrolled in this course")

        # Auto-select teacher with fallback strategy
        teacher = (
            db.query(Teacher).filter(
                and_(Teacher.course_id == request.course_id, Teacher.is_available == True)
            ).first()
            or
            db.query(Teacher).filter(Teacher.is_available == True).first()
            or
            db.query(Teacher).first()
        )

        if not teacher:
            raise HTTPException(status_code=400, detail="No teachers available")

        # Auto-select time slot with fallback strategy
        time_slot = (
            db.query(TimeSlot).filter(
                and_(TimeSlot.teacher_id == teacher.id, TimeSlot.is_available == True)
            ).first()
            or
            db.query(TimeSlot).filter(TimeSlot.is_available == True).first()
            or
            db.query(TimeSlot).first()
        )

        if not time_slot:
            raise HTTPException(status_code=400, detail="No time slots available")

        # Create enrollment
        enrollment = Enrollment(
            student_id=current_user["id"],
            course_id=request.course_id,
            teacher_id=teacher.id,
            time_slot_id=time_slot.id,
            start_date=datetime.now().date(),
            status="pending"  # Pending payment approval
        )
        db.add(enrollment)
        db.flush()

        # Create payment record (status pending)
        payment = Payment(
            enrollment_id=enrollment.id,
            amount=course.fee,
            currency=course.currency,
            status="pending",
            payment_method="pending"
        )
        db.add(payment)
        db.flush()

        # Try to create Zoom meeting
        try:
            zoom_response = create_zoom_meeting(
                course_name=course.name,
                teacher_name=teacher.user.name,
                start_time=f"{time_slot.day_of_week} {time_slot.start_time}"
            )
            if zoom_response:
                enrollment.meeting_link = zoom_response.get("join_url", "")
        except Exception as e:
            print(f"Zoom meeting creation failed: {str(e)}")

        db.commit()

        return {
            "id": enrollment.id,
            "status": "pending",
            "teacher": {
                "id": teacher.id,
                "name": teacher.user.name
            },
            "time_slot": {
                "id": time_slot.id,
                "day": time_slot.day_of_week,
                "start_time": time_slot.start_time,
                "end_time": time_slot.end_time
            },
            "payment": {
                "amount": course.fee,
                "currency": course.currency,
                "status": "pending"
            },
            "message": "Enrollment created. Please submit payment proof for approval."
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error in quick_enroll: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit-payment-proof")
async def submit_payment_proof(
    enrollment_id: int = Form(...),
    reference_number: str = Form(...),
    payment_method: str = Form(...),
    proof_file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit payment proof for enrollment approval"""
    try:
        # Verify enrollment exists and belongs to user
        enrollment = db.query(Enrollment).filter(
            and_(
                Enrollment.id == enrollment_id,
                Enrollment.student_id == current_user["id"]
            )
        ).first()

        if not enrollment:
            raise HTTPException(status_code=404, detail="Enrollment not found")

        if enrollment.status != "pending":
            raise HTTPException(status_code=400, detail="Enrollment already processed")

        # Save uploaded file
        file_ext = Path(proof_file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = UPLOAD_DIR / unique_filename

        with open(file_path, "wb") as f:
            content = await proof_file.read()
            f.write(content)

        # Create payment proof record
        proof = PaymentProof(
            enrollment_id=enrollment.id,
            reference_number=reference_number,
            payment_method=payment_method,
            proof_file_path=str(file_path),
            status="pending"
        )
        db.add(proof)

        # Update payment record
        payment = db.query(Payment).filter(Payment.enrollment_id == enrollment.id).first()
        if payment:
            payment.payment_method = payment_method
            payment.reference_number = reference_number
            payment.status = "pending_approval"

        # Update enrollment status
        enrollment.status = "pending_admin_approval"

        db.commit()

        # Send notification to admin
        admin_users = db.query(User).filter(User.role == "admin").all()
        notification_service = NotificationService()

        for admin in admin_users:
            notification = Notification(
                recipient_id=admin.id,
                sender_id=current_user["id"],
                type="payment_proof_submission",
                title="New Payment Proof Submitted",
                message=f"{current_user['name']} submitted payment proof for {enrollment.course.name}",
                metadata={
                    "enrollment_id": enrollment.id,
                    "reference_number": reference_number,
                    "payment_method": payment_method
                },
                is_read=False
            )
            db.add(notification)

        db.commit()

        return {
            "status": "success",
            "message": "Payment proof submitted successfully. Awaiting admin approval.",
            "enrollment_id": enrollment.id,
            "reference_number": reference_number
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error submitting payment proof: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending")
async def get_pending_enrollments(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get pending enrollment for current student"""
    enrollments = db.query(Enrollment).filter(
        and_(
            Enrollment.student_id == current_user["id"],
            Enrollment.status.in_(["pending", "pending_admin_approval"])
        )
    ).all()

    result = []
    for enrollment in enrollments:
        payment_proof = db.query(PaymentProof).filter(
            PaymentProof.enrollment_id == enrollment.id
        ).first()

        result.append({
            "id": enrollment.id,
            "course": {
                "id": enrollment.course.id,
                "name": enrollment.course.name,
                "fee": enrollment.course.fee
            },
            "teacher": {
                "id": enrollment.teacher.id,
                "name": enrollment.teacher.user.name
            },
            "time_slot": {
                "day": enrollment.time_slot.day_of_week,
                "start_time": enrollment.time_slot.start_time,
                "end_time": enrollment.time_slot.end_time
            },
            "status": enrollment.status,
            "payment_proof": {
                "reference_number": payment_proof.reference_number if payment_proof else None,
                "payment_method": payment_proof.payment_method if payment_proof else None,
                "status": payment_proof.status if payment_proof else None
            } if payment_proof else None
        })

    return result


@router.get("/my-enrollments")
async def get_my_enrollments(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all enrollments for current student"""
    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == current_user["id"]
    ).order_by(Enrollment.created_at.desc()).all()

    result = []
    for enrollment in enrollments:
        payment = db.query(Payment).filter(Payment.enrollment_id == enrollment.id).first()
        payment_proof = db.query(PaymentProof).filter(
            PaymentProof.enrollment_id == enrollment.id
        ).first()

        result.append({
            "id": enrollment.id,
            "course": {
                "id": enrollment.course.id,
                "name": enrollment.course.name,
                "fee": enrollment.course.fee
            },
            "teacher": {
                "id": enrollment.teacher.id,
                "name": enrollment.teacher.user.name
            },
            "time_slot": {
                "day": enrollment.time_slot.day_of_week,
                "start_time": enrollment.time_slot.start_time,
                "end_time": enrollment.time_slot.end_time
            },
            "status": enrollment.status,
            "meeting_link": enrollment.meeting_link,
            "start_date": enrollment.start_date.isoformat(),
            "payment": {
                "amount": payment.amount if payment else 0,
                "currency": payment.currency if payment else "PKR",
                "status": payment.status if payment else "pending",
                "reference_number": payment.reference_number if payment else None
            },
            "payment_proof": {
                "reference_number": payment_proof.reference_number if payment_proof else None,
                "payment_method": payment_proof.payment_method if payment_proof else None,
                "status": payment_proof.status if payment_proof else None
            } if payment_proof else None
        })

    return result


@router.post("/approve-enrollment/{enrollment_id}")
async def approve_enrollment(
    enrollment_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin endpoint to approve enrollment"""
    # Check if user is admin
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Only admins can approve enrollments")

    try:
        enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
        if not enrollment:
            raise HTTPException(status_code=404, detail="Enrollment not found")

        # Update enrollment status
        enrollment.status = "active"

        # Update payment status
        payment = db.query(Payment).filter(Payment.enrollment_id == enrollment.id).first()
        if payment:
            payment.status = "completed"

        # Update payment proof status
        payment_proof = db.query(PaymentProof).filter(
            PaymentProof.enrollment_id == enrollment.id
        ).first()
        if payment_proof:
            payment_proof.status = "approved"

        # Add student to course group
        course_group = db.query(CourseGroup).filter(
            CourseGroup.course_id == enrollment.course_id
        ).first()

        if course_group:
            student_group = StudentCourseGroup(
                student_id=enrollment.student_id,
                course_group_id=course_group.id
            )
            db.add(student_group)

        # Send notification to student
        student = db.query(User).filter(User.id == enrollment.student_id).first()
        notification_service = NotificationService()

        notification = Notification(
            recipient_id=enrollment.student_id,
            sender_id=current_user["id"],
            type="enrollment_approved",
            title="Enrollment Approved",
            message=f"Your enrollment for {enrollment.course.name} has been approved! You can now join the class.",
            metadata={
                "enrollment_id": enrollment.id,
                "course_id": enrollment.course_id
            },
            is_read=False
        )
        db.add(notification)

        db.commit()

        return {
            "status": "success",
            "message": "Enrollment approved successfully",
            "enrollment_id": enrollment.id
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error approving enrollment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reject-enrollment/{enrollment_id}")
async def reject_enrollment(
    enrollment_id: int,
    reason: str = Form(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin endpoint to reject enrollment"""
    # Check if user is admin
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Only admins can reject enrollments")

    try:
        enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
        if not enrollment:
            raise HTTPException(status_code=404, detail="Enrollment not found")

        # Update statuses
        enrollment.status = "rejected"

        payment = db.query(Payment).filter(Payment.enrollment_id == enrollment.id).first()
        if payment:
            payment.status = "failed"

        payment_proof = db.query(PaymentProof).filter(
            PaymentProof.enrollment_id == enrollment.id
        ).first()
        if payment_proof:
            payment_proof.status = "rejected"

        # Send notification to student
        notification = Notification(
            recipient_id=enrollment.student_id,
            sender_id=current_user["id"],
            type="enrollment_rejected",
            title="Enrollment Rejected",
            message=f"Your enrollment for {enrollment.course.name} was rejected. Reason: {reason}",
            metadata={
                "enrollment_id": enrollment.id,
                "rejection_reason": reason
            },
            is_read=False
        )
        db.add(notification)

        db.commit()

        return {
            "status": "success",
            "message": "Enrollment rejected",
            "enrollment_id": enrollment.id
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error rejecting enrollment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
