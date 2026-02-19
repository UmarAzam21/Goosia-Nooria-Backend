from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import random
import string
from datetime import datetime

from database import get_db
from models import Payment, Enrollment, User, UserRole, PaymentStatus, Notification, EnrollmentStatus
from schemas import PaymentCreate, PaymentResponse
from auth import get_current_user, require_role

router = APIRouter()

# Payment account details
PAYMENT_ACCOUNTS = {
    "jazzcash": {
        "account_title": "Jamia Gosia Nooria",
        "account_number": "03001234567",
        "note": "Send payment to this JazzCash number and enter transaction ID"
    },
    "easypaisa": {
        "account_title": "Jamia Gosia Nooria",
        "account_number": "03001234567",
        "note": "Send payment to this Easypaisa number and enter transaction ID"
    },
    "bank_transfer": {
        "bank_name": "Meezan Bank",
        "account_title": "Jamia Gosia Nooria",
        "account_number": "01234567890123",
        "iban": "PK12MEZN0001234567890123",
        "branch": "Main Branch, Lahore",
        "note": "Transfer to this bank account and provide transaction reference"
    }
}

def generate_batch_number():
    """Generate unique batch number for receipt"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"MGN-{timestamp}-{random_str}"

@router.get("/payment-details")
def get_payment_details(payment_method: str):
    """Get payment account details for JazzCash, Easypaisa, or Bank Transfer"""
    if payment_method not in PAYMENT_ACCOUNTS:
        raise HTTPException(status_code=400, detail="Invalid payment method")
    
    return {
        "payment_method": payment_method,
        "details": PAYMENT_ACCOUNTS[payment_method]
    }

@router.post("/submit-payment")
def submit_payment(
    enrollment_id: int,
    transaction_id: str,
    payment_proof_url: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit payment with transaction ID after paying via JazzCash/Easypaisa/Bank"""
    # Get enrollment and verify ownership
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    if current_user.role == UserRole.STUDENT and enrollment.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get payment record
    payment = db.query(Payment).filter(Payment.enrollment_id == enrollment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment.payment_status == PaymentStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Payment already completed")
    
    # Update payment with transaction details
    payment.transaction_id = transaction_id
    payment.payment_proof_url = payment_proof_url
    payment.payment_status = PaymentStatus.PENDING  # Admin will verify
    
    db.commit()
    db.refresh(payment)
    
    return {
        "message": "Payment details submitted successfully. Admin will verify and confirm.",
        "payment": payment
    }

@router.post("/confirm-payment/{payment_id}")
def confirm_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Confirm payment and generate batch number (Admin only)"""
    try:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        # Generate batch number
        batch_number = generate_batch_number()
        
        payment.payment_status = PaymentStatus.COMPLETED
        payment.batch_number = batch_number
        payment.paid_at = datetime.now()
        
        # Update enrollment payment status
        enrollment = db.query(Enrollment).filter(Enrollment.id == payment.enrollment_id).first()
        if enrollment:
            enrollment.payment_status = PaymentStatus.COMPLETED
            enrollment.enrollment_status = EnrollmentStatus.APPROVED
            
            # Create notification for teacher about new enrollment
            try:
                if enrollment.teacher and enrollment.teacher.user:
                    teacher_user = enrollment.teacher.user
                    notification = Notification(
                        user_id=teacher_user.id,
                        title="New Student Enrolled",
                        message=f"Student '{enrollment.student.name}' (Email: {enrollment.student.email}, Phone: {enrollment.student.phone}) has enrolled in your '{enrollment.course.name}' class. Schedule: {enrollment.time_slot.day_of_week} at {enrollment.time_slot.start_time}.",
                        type="enrollment_notification"
                    )
                    db.add(notification)
            except Exception as e:
                print(f"Warning: Could not create notification - {str(e)}")
                # Continue with payment confirmation even if notification fails
        
        db.commit()
        db.refresh(payment)
        
        return {
            "message": "Payment confirmed successfully. Student enrollment is now active and teacher has been notified.",
            "batch_number": batch_number,
            "payment_id": payment.id,
            "payment_status": payment.payment_status
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error confirming payment: {str(e)}")

@router.get("/receipt/{payment_id}")
def get_payment_receipt(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payment receipt with batch number"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    enrollment = db.query(Enrollment).filter(Enrollment.id == payment.enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    # Verify access
    if current_user.role == UserRole.STUDENT and enrollment.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if payment.payment_status != PaymentStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Payment not completed yet")
    
    return {
        "receipt": {
            "batch_number": payment.batch_number,
            "amount": payment.amount,
            "payment_method": payment.payment_method,
            "transaction_id": payment.transaction_id,
            "paid_at": payment.paid_at,
            "student_name": enrollment.student.name,
            "course_name": enrollment.course.name,
            "status": "PAID"
        }
    }

@router.get("/my-payments", response_model=List[PaymentResponse])
def get_my_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all payments for current user"""
    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id
    ).all()
    
    enrollment_ids = [e.id for e in enrollments]
    payments = db.query(Payment).filter(Payment.enrollment_id.in_(enrollment_ids)).all()
    
    return payments
