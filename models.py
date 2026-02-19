from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum, Date, Time, JSON, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class UserRole(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class PaymentMethod(str, enum.Enum):
    JAZZCASH = "jazzcash"
    EASYPAISA = "easypaisa"
    BANK_TRANSFER = "bank_transfer"
    AT_MASJID = "at_masjid"

class ClassStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class AttendanceStatus(str, enum.Enum):
    PENDING = "pending"
    PRESENT = "present"
    ABSENT = "absent"

class EnrollmentStatus(str, enum.Enum):
    PENDING_TEACHER = "pending_teacher"  # Waiting for teacher approval
    APPROVED = "approved"  # Teacher approved, classes active
    REJECTED = "rejected"  # Teacher rejected

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole, native_enum=False), nullable=False, default=UserRole.STUDENT)
    phone = Column(String, nullable=True)
    country = Column(String, nullable=True)  # e.g., "Pakistan"
    city = Column(String, nullable=True)      # e.g., "Karachi"
    timezone = Column(String, default="UTC")  # e.g., "Asia/Karachi"
    frozen_by_admin = Column(Boolean, default=False)
    freeze_reason = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    student_enrollments = relationship("Enrollment", back_populates="student", foreign_keys="Enrollment.student_id")
    teacher_profile = relationship("Teacher", back_populates="user", uselist=False)
    sent_messages = relationship("ChatMessage", back_populates="sender", foreign_keys="ChatMessage.sender_id")
    notification_preferences = relationship("NotificationPreference", back_populates="user", uselist=False)
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False)

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    duration_weeks = Column(Integer, nullable=False)  # Course duration in weeks
    fee = Column(Float, nullable=False)
    currency = Column(String, default="USD")  # USD, PKR, GBP, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    teachers = relationship("Teacher", back_populates="course")
    enrollments = relationship("Enrollment", back_populates="course")
    groups = relationship("CourseGroup", back_populates="course")
    coupons = relationship("Coupon", secondary="coupon_courses", back_populates="courses")

class Teacher(Base):
    __tablename__ = "teachers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    bio = Column(Text)
    experience_years = Column(Integer)
    qualification = Column(String)
    is_available = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="teacher_profile")
    course = relationship("Course", back_populates="teachers")
    time_slots = relationship("TimeSlot", back_populates="teacher")
    enrollments = relationship("Enrollment", back_populates="teacher")

class TimeSlot(Base):
    __tablename__ = "time_slots"
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    day_of_week = Column(String)  # Monday, Tuesday, etc.
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_available = Column(Boolean, default=True)
    
    # Relationships
    teacher = relationship("Teacher", back_populates="time_slots")
    enrollments = relationship("Enrollment", back_populates="time_slot")

class Enrollment(Base):
    __tablename__ = "enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    time_slot_id = Column(Integer, ForeignKey("time_slots.id"))
    payment_method = Column(Enum(PaymentMethod, native_enum=False), nullable=False)
    payment_status = Column(Enum(PaymentStatus, native_enum=False), default=PaymentStatus.PENDING)
    enrollment_status = Column(Enum(EnrollmentStatus, native_enum=False), default=EnrollmentStatus.PENDING_TEACHER)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)
    zoom_link = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student = relationship("User", back_populates="student_enrollments", foreign_keys=[student_id])
    course = relationship("Course", back_populates="enrollments")
    teacher = relationship("Teacher", back_populates="enrollments")
    time_slot = relationship("TimeSlot", back_populates="enrollments")
    payment = relationship("Payment", back_populates="enrollment", uselist=False)
    classes = relationship("Class", back_populates="enrollment")
    group = relationship("CourseGroup", back_populates="enrollment", uselist=False)
    certificate = relationship("Certificate", back_populates="enrollment", uselist=False)

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"), unique=True)
    amount = Column(Float, nullable=False)
    payment_method = Column(Enum(PaymentMethod, native_enum=False), nullable=False)
    payment_status = Column(Enum(PaymentStatus, native_enum=False), default=PaymentStatus.PENDING)
    transaction_id = Column(String, nullable=True)  # JazzCash/Easypaisa/Bank transaction ID
    payment_proof_url = Column(String, nullable=True)  # Screenshot/receipt URL
    batch_number = Column(String, nullable=True)  # Receipt batch number
    paid_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    enrollment = relationship("Enrollment", back_populates="payment")

class Class(Base):
    __tablename__ = "classes"
    
    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"))
    class_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    zoom_link = Column(String, nullable=True)
    meeting_id = Column(String, nullable=True)
    status = Column(Enum(ClassStatus, native_enum=False), default=ClassStatus.SCHEDULED)
    attendance_status = Column(Enum(AttendanceStatus, native_enum=False), default=AttendanceStatus.PENDING)
    recorded_lecture_url = Column(String, nullable=True)
    notes_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    enrollment = relationship("Enrollment", back_populates="classes")
    messages = relationship("ChatMessage", back_populates="class_session")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    sender = relationship("User", back_populates="sent_messages", foreign_keys=[sender_id])
    class_session = relationship("Class", back_populates="messages")

class NotificationPreference(Base):
    __tablename__ = "notification_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    enable_email_notifications = Column(Boolean, default=True)
    enable_sms_notifications = Column(Boolean, default=True)
    enable_voice_notifications = Column(Boolean, default=True)  # Voice alerts for important notifications
    enable_class_reminders = Column(Boolean, default=True)
    enable_payment_reminders = Column(Boolean, default=True)
    enable_new_enrollment_notifications = Column(Boolean, default=True)
    notification_time = Column(String, default="09:00")  # Time to send scheduled notifications (HH:MM format)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notification_preferences")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String, nullable=True)  # 'new_student', 'payment_approved', 'class_reminder', etc.
    is_important = Column(Boolean, default=False)  # Flag for important notifications
    should_notify_voice = Column(Boolean, default=False)  # Send voice notification for this
    scheduled_time = Column(DateTime(timezone=True), nullable=True)  # When to send the notification
    is_read = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
class Coupon(Base):
    __tablename__ = "coupons"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)
    discount_type = Column(String, nullable=False)  # 'percentage' or 'fixed'
    discount_value = Column(Float, nullable=False)  # Percentage or amount
    max_uses = Column(Integer, nullable=True)  # None = unlimited
    current_uses = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    courses = relationship("Course", secondary="coupon_courses", back_populates="coupons")
    creator = relationship("User", foreign_keys=[created_by])

# Association table for coupon-course many-to-many relationship
coupon_courses = Table(
    'coupon_courses',
    Base.metadata,
    Column('coupon_id', Integer, ForeignKey('coupons.id')),
    Column('course_id', Integer, ForeignKey('courses.id'))
)

class CourseGroup(Base):
    __tablename__ = "course_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"))
    group_name = Column(String, nullable=False)  # e.g., "Advanced Quran - Group 1"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    course = relationship("Course", back_populates="groups")
    enrollment = relationship("Enrollment", back_populates="group")
    messages = relationship("GroupMessage", back_populates="group")

class GroupMessage(Base):
    __tablename__ = "group_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("course_groups.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text, nullable=False)
    attachment_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    group = relationship("CourseGroup", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id])

class StudentProfile(Base):
    __tablename__ = "student_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    bio = Column(Text, nullable=True)
    profile_picture_url = Column(String, nullable=True)
    total_courses_completed = Column(Integer, default=0)
    total_hours_learned = Column(Float, default=0)
    total_spent = Column(Float, default=0)
    preferred_language = Column(String, default="en")
    notify_via_email = Column(Boolean, default=True)
    notify_via_sms = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="student_profile")

class Certificate(Base):
    __tablename__ = "certificates"
    
    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    certificate_number = Column(String, unique=True, nullable=False)
    issued_date = Column(Date, nullable=False)
    completion_percentage = Column(Integer, nullable=False)
    certificate_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    enrollment = relationship("Enrollment", back_populates="certificate")
    student = relationship("User", foreign_keys=[student_id])
    course = relationship("Course", foreign_keys=[course_id])