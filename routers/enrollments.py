from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta, time

from database import get_db
from models import Enrollment, Course, Teacher, TimeSlot, Payment, User, PaymentStatus, UserRole, EnrollmentStatus, Notification, Class, ClassStatus, CourseGroup
from schemas import EnrollmentCreate, EnrollmentResponse, QuickEnrollRequest
from auth import get_current_user

# Try to use real Zoom API, fall back to simple meeting IDs if not configured
try:
    from zoom_api_service import create_zoom_meeting_via_api
    USE_ZOOM_API = True
except ImportError:
    USE_ZOOM_API = False

from zoom_service import create_zoom_meeting

router = APIRouter()

# Simple enrollment endpoint for student portal
@router.post("/quick-enroll", status_code=status.HTTP_201_CREATED)
def quick_enroll_course(
    request: QuickEnrollRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Quick enroll in a course (auto-selects teacher and time slot)"""
    try:
        course_id = request.course_id
        if not course_id:
            raise HTTPException(status_code=400, detail="course_id is required")
        
        # Verify course exists
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Get the selected time slot
        time_slot = db.query(TimeSlot).filter(TimeSlot.id == request.time_slot_id).first()
        if not time_slot:
            raise HTTPException(status_code=404, detail="Time slot not found")
        
        # Get the teacher from the time slot
        teacher = db.query(Teacher).filter(Teacher.id == time_slot.teacher_id).first()
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found for the selected time slot")
        
        # Calculate dates
        start_date = datetime.now().date()
        end_date = start_date + timedelta(weeks=course.duration_weeks if course.duration_weeks else 4)
        
        # Create enrollment (inactive until payment is approved)
        db_enrollment = Enrollment(
            student_id=current_user.id,
            course_id=course.id,
            teacher_id=teacher.id,
            time_slot_id=time_slot.id,
            payment_method="at_masjid",
            start_date=start_date,
            end_date=end_date,
            payment_status=PaymentStatus.PENDING,
            enrollment_status=EnrollmentStatus.PENDING_TEACHER,
            is_active=False,
            zoom_link=""
        )
        db.add(db_enrollment)
        db.flush()
        
        # Create payment record
        payment = Payment(
            enrollment_id=db_enrollment.id,
            amount=course.fee,
            payment_method="pending",
            payment_status="PENDING"
        )
        db.add(payment)
        db.commit()
        db.refresh(db_enrollment)
        
        return {
            "id": db_enrollment.id,
            "student_id": db_enrollment.student_id,
            "course_id": db_enrollment.course_id,
            "teacher_id": db_enrollment.teacher_id,
            "time_slot_id": db_enrollment.time_slot_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "is_active": False,
            "status": "pending",
            "payment_status": "pending"
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error in quick_enroll: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Enrollment failed: {str(e)}")

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
    
    # Create Zoom Meeting for this enrollment
    # Format: Simple meeting IDs based on enrollment ID
    event_name = f"{course.name}"
    start_datetime = datetime.combine(enrollment.start_date, time(9, 0))  # 9 AM default
    end_datetime = start_datetime + timedelta(hours=1)  # 1 hour duration
    
    # Create enrollment first without zoom_link
    db_enrollment = Enrollment(
        student_id=current_user.id,
        course_id=enrollment.course_id,
        teacher_id=enrollment.teacher_id,
        time_slot_id=enrollment.time_slot_id,
        payment_method=enrollment.payment_method,
        start_date=enrollment.start_date,
        end_date=end_date,
        payment_status=PaymentStatus.PENDING if enrollment.payment_method == "at_masjid" else PaymentStatus.PENDING,
        zoom_link=""  # Will be set below
    )
    db.add(db_enrollment)
    db.commit()
    db.refresh(db_enrollment)
    
    # Now create the Zoom meeting with enrollment ID for uniqueness
    start_datetime = datetime.combine(enrollment.start_date, time(9, 0))
    
    zoom_result = None
    
    # Try to use real Zoom API first
    if USE_ZOOM_API:
        zoom_result = create_zoom_meeting_via_api(
            event_name=event_name,
            start_time=start_datetime,
            duration_minutes=60
        )
    
    # Fall back to simple meeting ID if API not available or failed
    if not zoom_result or not zoom_result.get("success"):
        print(f"ℹ️  Using fallback Zoom meeting ID (Zoom API not configured)")
        zoom_result = create_zoom_meeting(
            event_name=event_name,
            start_time=start_datetime,
            end_time=start_datetime + timedelta(hours=1),
            description=f"Online class for {course.name}",
            event_id=str(db_enrollment.id)
        )
    
    if not zoom_result["success"]:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create Zoom meeting: {zoom_result.get('error', 'Unknown error')}"
        )
    
    # Update enrollment with final zoom_link
    zoom_link = zoom_result.get("zoom_link")
    db_enrollment.zoom_link = zoom_link
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
                meeting_id=zoom_result.get("meeting_id"),
                zoom_link=zoom_link,
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
        payment_method=enrollment.payment_method or "pending",
        payment_status="PENDING"
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

@router.get("/my-enrollments")
async def get_my_enrollments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all enrollments for the current user"""
    try:
        from sqlalchemy.orm import joinedload
        
        # Query with eager loading of relationships
        enrollments = db.query(Enrollment).filter(
            Enrollment.student_id == current_user.id
        ).options(
            joinedload(Enrollment.course),
            joinedload(Enrollment.teacher).joinedload(Teacher.user),
            joinedload(Enrollment.time_slot),
            joinedload(Enrollment.payment)
        ).all()
        
        result = []
        for enrollment in enrollments:
            try:
                payment = enrollment.payment
                
                enrollment_data = {
                    "id": enrollment.id,
                    "student_id": enrollment.student_id,
                    "course_id": enrollment.course_id,
                    "teacher_id": enrollment.teacher_id,
                    "time_slot_id": enrollment.time_slot_id,
                    "payment_method": enrollment.payment_method,
                    "payment_status": enrollment.payment_status,
                    "enrollment_status": enrollment.enrollment_status,
                    "start_date": enrollment.start_date.isoformat() if enrollment.start_date else None,
                    "end_date": enrollment.end_date.isoformat() if enrollment.end_date else None,
                    "is_active": enrollment.is_active,
                    "created_at": enrollment.created_at.isoformat() if enrollment.created_at else None,
                    "zoom_link": enrollment.zoom_link,
                }
                
                # Safely add optional relationships
                if enrollment.course:
                    enrollment_data["course"] = {
                        "id": enrollment.course.id,
                        "name": enrollment.course.name,
                        "fee": enrollment.course.fee,
                        "currency": "PKR"
                    }
                
                if enrollment.teacher and enrollment.teacher.user:
                    enrollment_data["teacher"] = {
                        "id": enrollment.teacher.id,
                        "name": enrollment.teacher.user.name
                    }
                
                if enrollment.time_slot:
                    enrollment_data["time_slot"] = {
                        "id": enrollment.time_slot.id,
                        "day": enrollment.time_slot.day_of_week,
                        "start_time": str(enrollment.time_slot.start_time),
                        "end_time": str(enrollment.time_slot.end_time)
                    }
                
                if payment:
                    enrollment_data["payment"] = {
                        "id": payment.id,
                        "amount": payment.amount,
                        "currency": "PKR",
                        "status": payment.payment_status,
                        "reference_number": payment.transaction_id,
                        "payment_proof_url": payment.payment_proof_url
                    }
                
                result.append(enrollment_data)
            except Exception as item_err:
                print(f"Error processing enrollment {enrollment.id}: {str(item_err)}")
                continue
        
        return result
    except Exception as e:
        print(f"Error fetching enrollments: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

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

@router.get("/admin/pending-approvals")
async def get_pending_approvals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get pending enrollment approvals for admin"""
    try:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Only admins can view pending approvals")

        enrollments = db.query(Enrollment).filter(
            Enrollment.is_active == False
        ).all()

        result = []
        for enrollment in enrollments:
            try:
                payment = db.query(Payment).filter(Payment.enrollment_id == enrollment.id).first()

                # Safe access to nested attributes
                student_name = enrollment.student.name if enrollment.student else "Unknown"
                student_email = enrollment.student.email if enrollment.student else "unknown@example.com"
                course_name = enrollment.course.name if enrollment.course else "Unknown Course"
                course_fee = enrollment.course.fee if enrollment.course else 0
                teacher_name = enrollment.teacher.user.name if (enrollment.teacher and enrollment.teacher.user) else "Unknown"

                result.append({
                    "id": enrollment.id,
                    "student": {
                        "id": enrollment.student_id,
                        "name": student_name,
                        "email": student_email
                    },
                    "course": {
                        "id": enrollment.course.id if enrollment.course else None,
                        "name": course_name,
                        "fee": course_fee
                    },
                    "teacher": {
                        "id": enrollment.teacher.id if enrollment.teacher else None,
                        "name": teacher_name
                    },
                    "time_slot": {
                        "day": enrollment.time_slot.day_of_week if enrollment.time_slot else "Unknown",
                        "start_time": str(enrollment.time_slot.start_time) if enrollment.time_slot else "00:00:00",
                        "end_time": str(enrollment.time_slot.end_time) if enrollment.time_slot else "00:00:00"
                    },
                    "status": enrollment.enrollment_status or "pending",
                    "payment": {
                        "amount": payment.amount if payment else 0,
                        "currency": "PKR",
                        "status": payment.payment_status if payment else "pending",
                        "reference_number": payment.transaction_id if payment else None
                    },
                    "payment_proof": {
                        "reference_number": payment.transaction_id if payment else None,
                        "payment_method": payment.payment_method if payment else None,
                        "proof_file_path": payment.payment_proof_url if payment else None
                    } if payment else None
                })
            except Exception as e:
                print(f"Error processing enrollment {enrollment.id}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue

        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_pending_approvals: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

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

# ===== PAYMENT APPROVAL ENDPOINTS =====

@router.post("/submit-payment-proof")
async def submit_payment_proof(
    enrollment_id: int = Form(...),
    reference_number: str = Form(...),
    payment_method: str = Form(...),
    proof_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit payment proof for enrollment approval"""
    from pathlib import Path
    import uuid
    
    try:
        # Verify enrollment exists and belongs to user
        enrollment = db.query(Enrollment).filter(
            Enrollment.id == enrollment_id,
            Enrollment.student_id == current_user.id
        ).first()

        if not enrollment:
            raise HTTPException(status_code=404, detail="Enrollment not found")

        if enrollment.is_active:
            raise HTTPException(status_code=400, detail="Enrollment already processed")

        # Save uploaded file
        UPLOAD_DIR = Path("uploads/payment_proofs")
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        
        file_ext = Path(proof_file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = UPLOAD_DIR / unique_filename
        
        with open(file_path, "wb") as f:
            content = await proof_file.read()
            f.write(content)

        # Update payment record
        payment = db.query(Payment).filter(Payment.enrollment_id == enrollment.id).first()
        if payment:
            payment.payment_method = payment_method
            payment.transaction_id = reference_number  # Store as transaction_id
            payment.payment_status = PaymentStatus.PENDING
            payment.payment_proof_url = str(file_path)

        # Update enrollment status
        enrollment.is_active = False  # Not active until approved

        db.commit()

        # Send notification to admins
        admin_users = db.query(User).filter(User.role == UserRole.ADMIN).all()

        for admin in admin_users:
            notification = Notification(
                user_id=admin.id,
                title="New Payment Proof Submitted",
                message=f"{current_user.name} submitted payment proof for {enrollment.course.name} - Ref: {reference_number}",
                type="payment_proof_submission"
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



@router.post("/approve-enrollment/{enrollment_id}")
async def approve_enrollment(
    enrollment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin endpoint to approve enrollment"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can approve enrollments")

    try:
        enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
        if not enrollment:
            raise HTTPException(status_code=404, detail="Enrollment not found")

        # Ensure enrollment has a valid zoom_link - create one if missing or invalid
        if not enrollment.zoom_link or "zoom.us/j/" not in str(enrollment.zoom_link):
            print(f"⚠️  Enrollment {enrollment_id} has invalid/missing zoom_link. Creating real Zoom meeting...")
            
            # Try to create a real Zoom meeting
            zoom_result = None
            if USE_ZOOM_API:
                start_datetime = datetime.combine(
                    enrollment.start_date or datetime.now().date(),
                    time(9, 0)
                )
                zoom_result = create_zoom_meeting_via_api(
                    event_name=f"{enrollment.course.name}",
                    start_time=start_datetime,
                    duration_minutes=60
                )
            
            # If API failed or not configured, use fallback
            if not zoom_result or not zoom_result.get("success"):
                print(f"⚠️  Using fallback Zoom meeting ID...")
                zoom_result = create_zoom_meeting(
                    event_name=f"{enrollment.course.name}",
                    start_time=datetime.combine(
                        enrollment.start_date or datetime.now().date(),
                        time(9, 0)
                    ),
                    end_time=datetime.combine(
                        enrollment.start_date or datetime.now().date(),
                        time(10, 0)
                    ),
                    description=f"Online class for {enrollment.course.name}",
                    event_id=str(enrollment.id)
                )
            
            if zoom_result and zoom_result.get("zoom_link"):
                enrollment.zoom_link = zoom_result.get("zoom_link")
                print(f"✅ Created Zoom meeting: {enrollment.zoom_link}")
            else:
                print(f"❌ Failed to create Zoom meeting, but proceeding with approval")

        # Update enrollment status and make active
        enrollment.is_active = True
        enrollment.enrollment_status = EnrollmentStatus.APPROVED

        # Update payment status
        payment = db.query(Payment).filter(Payment.enrollment_id == enrollment.id).first()
        if payment:
            payment.payment_status = PaymentStatus.COMPLETED
            payment.paid_at = datetime.now()

        # Add student to course group
        course_group = db.query(CourseGroup).filter(
            CourseGroup.course_id == enrollment.course_id
        ).first()

        if not course_group:
            # Create course group if doesn't exist
            course_group = CourseGroup(
                course_id=enrollment.course_id,
                enrollment_id=enrollment.id,
                group_name=f"{enrollment.course.name} - Group {enrollment.id}"
            )
            db.add(course_group)
            db.flush()

        # Send notification to student with zoom link
        notification = Notification(
            user_id=enrollment.student_id,
            title="Enrollment Approved",
            message=f"Your enrollment for {enrollment.course.name} has been approved! You can now join the class. Meeting link: {enrollment.zoom_link}",
            type="enrollment_approved"
        )
        db.add(notification)

        db.commit()

        return {
            "status": "success",
            "message": "Enrollment approved successfully",
            "enrollment_id": enrollment.id,
            "zoom_link": enrollment.zoom_link
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error approving enrollment: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reject-enrollment/{enrollment_id}")
async def reject_enrollment(
    enrollment_id: int,
    reason: str = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin endpoint to reject enrollment"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can reject enrollments")

    try:
        enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
        if not enrollment:
            raise HTTPException(status_code=404, detail="Enrollment not found")

        # Update statuses
        enrollment.enrollment_status = EnrollmentStatus.REJECTED
        enrollment.is_active = False

        payment = db.query(Payment).filter(Payment.enrollment_id == enrollment.id).first()
        if payment:
            payment.payment_status = PaymentStatus.FAILED

        # Send notification to student
        notification_msg = f"Your enrollment for {enrollment.course.name} was rejected."
        if reason:
            notification_msg += f" Reason: {reason}"

        notification = Notification(
            user_id=enrollment.student_id,
            title="Enrollment Rejected",
            message=notification_msg,
            type="enrollment_rejected"
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