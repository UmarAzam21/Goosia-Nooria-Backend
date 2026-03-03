from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date, time
from models import UserRole, PaymentStatus, PaymentMethod, ClassStatus, AttendanceStatus

# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr
    city: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.STUDENT

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    role: UserRole
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Course Schemas
class CourseBase(BaseModel):
    name: str
    description: Optional[str] = None
    duration_weeks: int
    fee: float
    currency: str = "USD"

class CourseCreate(CourseBase):
    pass

class CourseResponse(CourseBase):
    id: int
    is_active: bool
    created_at: datetime
    teacher_id: Optional[int] = None
    enrolled_count: Optional[int] = None
    
    class Config:
        from_attributes = True

# Teacher Schemas
class TeacherBase(BaseModel):
    bio: Optional[str] = None
    experience_years: Optional[int] = None
    qualification: Optional[str] = None

class TeacherCreate(TeacherBase):
    user_id: int
    course_id: Optional[int] = None

class TeacherResponse(TeacherBase):
    id: int
    user_id: int
    course_id: Optional[int] = None
    is_available: bool
    user: UserResponse
    
    class Config:
        from_attributes = True

# TimeSlot Schemas
class TimeSlotBase(BaseModel):
    day_of_week: str
    start_time: time
    end_time: time

class TimeSlotCreate(TimeSlotBase):
    teacher_id: int

class TimeSlotResponse(TimeSlotBase):
    id: int
    teacher_id: int
    is_available: bool
    
    class Config:
        from_attributes = True

# Enrollment Schemas
class QuickEnrollRequest(BaseModel):
    course_id: int
    time_slot_id: int

class EnrollmentCreate(BaseModel):
    course_id: int
    teacher_id: int
    time_slot_id: int
    payment_method: PaymentMethod
    start_date: date

class EnrollmentResponse(BaseModel):
    id: int
    student_id: int
    course_id: int
    teacher_id: int
    time_slot_id: int
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    enrollment_status: str
    start_date: date
    end_date: date
    is_active: bool
    created_at: datetime
    zoom_link: Optional[str] = None
    course: CourseResponse
    teacher: TeacherResponse
    time_slot: TimeSlotResponse
    payment: Optional['PaymentResponse'] = None
    
    class Config:
        from_attributes = True

# Payment Schemas
class PaymentCreate(BaseModel):
    enrollment_id: int
    amount: float
    payment_method: PaymentMethod
    transaction_id: Optional[str] = None
    payment_proof_url: Optional[str] = None

class PaymentResponse(BaseModel):
    id: int
    enrollment_id: int
    amount: float
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    transaction_id: Optional[str] = None
    payment_proof_url: Optional[str] = None
    batch_number: Optional[str] = None
    paid_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Class Schemas
class ClassBase(BaseModel):
    class_date: date
    start_time: time
    end_time: time

class ClassCreate(ClassBase):
    enrollment_id: int
    zoom_link: Optional[str] = None
    meeting_id: Optional[str] = None

class ClassResponse(ClassBase):
    id: int
    enrollment_id: int
    zoom_link: Optional[str] = None
    meeting_id: Optional[str] = None
    status: ClassStatus
    attendance_status: AttendanceStatus
    recorded_lecture_url: Optional[str] = None
    notes_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ClassWithDetails(ClassResponse):
    student_name: str
    teacher_name: str
    course_name: str
    zoom_link: Optional[str] = None

# Chat Schemas
class ChatMessageCreate(BaseModel):
    class_id: Optional[int] = None
    receiver_id: Optional[int] = None
    message: str

class ChatMessageResponse(BaseModel):
    id: int
    class_id: Optional[int] = None
    sender_id: int
    receiver_id: Optional[int] = None
    message: str
    is_read: bool
    created_at: datetime
    sender_name: str
    
    class Config:
        from_attributes = True

# Dashboard Schemas
class StudentDashboard(BaseModel):
    enrollments: List[EnrollmentResponse]
    today_classes: List[ClassWithDetails]
    upcoming_classes: List[ClassWithDetails]

class TeacherDashboard(BaseModel):
    today_classes: List[ClassWithDetails]
    upcoming_classes: List[ClassWithDetails]
    total_students: int

class AdminDashboard(BaseModel):
    total_students: int
    total_teachers: int
    total_courses: int
    total_enrollments: int
    pending_payments: int
    today_classes: int

# Notification Schemas
class NotificationPreferenceBase(BaseModel):
    enable_email_notifications: bool = True
    enable_sms_notifications: bool = True
    enable_voice_notifications: bool = True
    enable_class_reminders: bool = True
    enable_payment_reminders: bool = True
    enable_new_enrollment_notifications: bool = True
    notification_time: str = "09:00"  # HH:MM format

class NotificationPreferenceCreate(NotificationPreferenceBase):
    user_id: int

class NotificationPreferenceResponse(NotificationPreferenceBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class NotificationCreate(BaseModel):
    title: str
    message: str
    type: Optional[str] = None
    is_important: bool = False
    should_notify_voice: bool = False
    scheduled_time: Optional[datetime] = None

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    type: Optional[str] = None
    is_important: bool
    should_notify_voice: bool
    scheduled_time: Optional[datetime] = None
    is_read: bool
    is_sent: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
# Coupon Schemas
class CouponBase(BaseModel):
    code: str
    description: Optional[str] = None
    discount_type: str  # 'percentage' or 'fixed'
    discount_value: float
    max_uses: Optional[int] = None
    is_active: bool = True
    expires_at: Optional[datetime] = None

class CouponCreate(CouponBase):
    pass

class CouponResponse(CouponBase):
    id: int
    current_uses: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# StudentProfile Schemas
class StudentProfileBase(BaseModel):
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None
    preferred_language: str = "en"
    notify_via_email: bool = True
    notify_via_sms: bool = False

class StudentProfileCreate(StudentProfileBase):
    pass

class StudentProfileResponse(StudentProfileBase):
    id: int
    user_id: int
    total_courses_completed: int
    total_hours_learned: float
    total_spent: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# CourseGroup Schemas
class CourseGroupBase(BaseModel):
    group_name: str
    is_active: bool = True

class CourseGroupCreate(CourseGroupBase):
    course_id: int
    enrollment_id: int

class CourseGroupResponse(CourseGroupBase):
    id: int
    course_id: int
    enrollment_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# GroupMessage Schemas
class GroupMessageBase(BaseModel):
    message: str
    attachment_url: Optional[str] = None

class GroupMessageCreate(GroupMessageBase):
    group_id: int

class GroupMessageResponse(GroupMessageBase):
    id: int
    group_id: int
    sender_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Certificate Schemas
class CertificateBase(BaseModel):
    completion_percentage: int

class CertificateCreate(CertificateBase):
    enrollment_id: int

class CertificateResponse(CertificateBase):
    id: int
    enrollment_id: int
    student_id: int
    course_id: int
    certificate_number: str
    issued_date: date
    certificate_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True