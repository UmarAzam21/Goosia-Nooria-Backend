from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, time
from pydantic import BaseModel

from database import get_db
from models import User, Teacher, UserRole, TimeSlot
from schemas import UserCreate, UserLogin, UserResponse, Token
from auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user
)

# Schema for profile update
class ProfileUpdate(BaseModel):
    name: str
    city: str | None = None

# Schema for admin teacher creation
class TeacherCreate(BaseModel):
    name: str
    email: str
    password: str

# Schema for admin teacher update
class TeacherUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    password: str | None = None

# Schema for teacher response
class TeacherResponse(BaseModel):
    id: str
    name: str
    email: str
    is_active: bool | None
    created_at: str | None
    
    class Config:
        from_attributes = True

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user.password)
        db_user = User(
            name=user.name,
            email=user.email,
            password_hash=hashed_password,
            role=user.role,
            city=user.city
        )
        db.add(db_user)
        db.flush()  # Get the ID without refreshing
        
        # If user is registering as a teacher, create teacher profile and time slots
        if user.role == UserRole.TEACHER or (hasattr(user.role, 'value') and user.role.value == 'teacher') or str(user.role).lower() == 'teacher':
            teacher_profile = Teacher(
                user_id=db_user.id,
                bio="",
                experience_years=0,
                qualification="",
                is_available=True
            )
            db.add(teacher_profile)
            db.flush()  # Get the teacher ID
            
            # Bulk create all time slots (no loops, no individual commits)
            time_slots_data = [
                TimeSlot(teacher_id=teacher_profile.id, day_of_week="Monday", start_time=time(9, 0), end_time=time(11, 0), is_available=True),
                TimeSlot(teacher_id=teacher_profile.id, day_of_week="Monday", start_time=time(11, 0), end_time=time(13, 0), is_available=True),
                TimeSlot(teacher_id=teacher_profile.id, day_of_week="Tuesday", start_time=time(14, 0), end_time=time(16, 0), is_available=True),
                TimeSlot(teacher_id=teacher_profile.id, day_of_week="Tuesday", start_time=time(16, 0), end_time=time(18, 0), is_available=True),
                TimeSlot(teacher_id=teacher_profile.id, day_of_week="Wednesday", start_time=time(9, 0), end_time=time(11, 0), is_available=True),
                TimeSlot(teacher_id=teacher_profile.id, day_of_week="Wednesday", start_time=time(11, 0), end_time=time(13, 0), is_available=True),
                TimeSlot(teacher_id=teacher_profile.id, day_of_week="Thursday", start_time=time(14, 0), end_time=time(16, 0), is_available=True),
                TimeSlot(teacher_id=teacher_profile.id, day_of_week="Thursday", start_time=time(16, 0), end_time=time(18, 0), is_available=True),
                TimeSlot(teacher_id=teacher_profile.id, day_of_week="Friday", start_time=time(9, 0), end_time=time(11, 0), is_available=True),
                TimeSlot(teacher_id=teacher_profile.id, day_of_week="Friday", start_time=time(11, 0), end_time=time(13, 0), is_available=True),
                TimeSlot(teacher_id=teacher_profile.id, day_of_week="Saturday", start_time=time(14, 0), end_time=time(16, 0), is_available=True),
                TimeSlot(teacher_id=teacher_profile.id, day_of_week="Saturday", start_time=time(16, 0), end_time=time(18, 0), is_available=True),
            ]
            db.add_all(time_slots_data)
        
        # Single commit for everything
        db.commit()
        
        print(f"[INFO] User registered successfully: {db_user.email} (ID: {db_user.id})")
        return db_user
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Registration error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login user and return access token"""
    # Find user
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        print(f"[ERROR] Login failed for email: {form_data.username}. User found: {user is not None}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is frozen by admin
    if user.frozen_by_admin:
        print(f"[ERROR] Login denied for frozen user: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account frozen by admin. Reason: {user.freeze_reason or 'No reason provided'}"
        )
    
    # Get role as string value
    role_value = user.role.value if hasattr(user.role, 'value') else str(user.role).lower()
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": role_value},
        expires_delta=access_token_expires
    )
    
    print(f"[INFO] User logged in successfully: {user.email} (ID: {user.id}, Role: {role_value})")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/login/json", response_model=Token)
def login_json(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user with JSON body"""
    user = db.query(User).filter(User.email == user_credentials.email).first()
    if not user or not verify_password(user_credentials.password, user.password_hash):
        print(f"[ERROR] Login failed for email: {user_credentials.email}. User found: {user is not None}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is frozen by admin
    if user.frozen_by_admin:
        print(f"[ERROR] Login denied for frozen user: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account frozen by admin. Reason: {user.freeze_reason or 'No reason provided'}"
        )
    
    # Get role as string value
    role_value = user.role.value if hasattr(user.role, 'value') else str(user.role).lower()
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": role_value},
        expires_delta=access_token_expires
    )
    
    print(f"[INFO] User logged in successfully (JSON): {user.email} (ID: {user.id}, Role: {role_value})")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

# Update user profile endpoint (using /users prefix pattern)
@router.put("/profile", response_model=UserResponse)
def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile information"""
    try:
        # Get the current user from database
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update allowed fields
        user.name = profile_data.name
        user.city = profile_data.city
        
        db.commit()
        db.refresh(user)
        
        print(f"[INFO] User profile updated: {user.email} (ID: {user.id})")
        return user
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to update profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")


# ===== ADMIN TEACHER MANAGEMENT ENDPOINTS =====

@router.post("/admin/teachers", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_teacher_admin(
    teacher_data: TeacherCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new teacher account (admin only)"""
    try:
        # Check if current user is admin
        role_value = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
        if role_value != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can create teacher accounts"
            )
        
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == teacher_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new teacher user
        hashed_password = get_password_hash(teacher_data.password)
        db_user = User(
            name=teacher_data.name,
            email=teacher_data.email,
            password_hash=hashed_password,
            role="teacher"
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Create teacher profile
        teacher_profile = Teacher(
            user_id=db_user.id,
            bio="",
            experience_years=0,
            qualification="",
            is_available=True
        )
        db.add(teacher_profile)
        db.commit()
        db.refresh(teacher_profile)
        
        # Create default time slots for the teacher
        time_slots_data = [
            {"day": "Monday", "start": time(9, 0), "end": time(11, 0)},
            {"day": "Monday", "start": time(11, 0), "end": time(13, 0)},
            {"day": "Tuesday", "start": time(14, 0), "end": time(16, 0)},
            {"day": "Tuesday", "start": time(16, 0), "end": time(18, 0)},
            {"day": "Wednesday", "start": time(9, 0), "end": time(11, 0)},
            {"day": "Wednesday", "start": time(11, 0), "end": time(13, 0)},
            {"day": "Thursday", "start": time(14, 0), "end": time(16, 0)},
            {"day": "Thursday", "start": time(16, 0), "end": time(18, 0)},
            {"day": "Friday", "start": time(9, 0), "end": time(11, 0)},
            {"day": "Friday", "start": time(11, 0), "end": time(13, 0)},
            {"day": "Saturday", "start": time(14, 0), "end": time(16, 0)},
            {"day": "Saturday", "start": time(16, 0), "end": time(18, 0)},
        ]
        
        for slot_data in time_slots_data:
            time_slot = TimeSlot(
                teacher_id=teacher_profile.id,
                day_of_week=slot_data["day"],
                start_time=slot_data["start"],
                end_time=slot_data["end"],
                is_available=True
            )
            db.add(time_slot)
        
        db.commit()
        print(f"[INFO] Teacher account created by admin: {db_user.email} (ID: {db_user.id})")
        return db_user
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to create teacher: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create teacher: {str(e)}")


@router.get("/admin/teachers")
def list_teachers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of all teachers (admin only)"""
    try:
        # Check if current user is admin
        role_value = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
        if role_value != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can view teacher list"
            )
        
        # Get all users with teacher role
        teachers = db.query(User).filter(
            (User.role == UserRole.TEACHER) | (User.role == "teacher")
        ).all()
        
        # Format response
        response = []
        for teacher in teachers:
            response.append({
                "id": teacher.id,
                "name": teacher.name,
                "email": teacher.email,
                "is_active": not teacher.frozen_by_admin if hasattr(teacher, 'frozen_by_admin') else True,
                "created_at": teacher.created_at.isoformat() if teacher.created_at else None,
            })
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to list teachers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list teachers: {str(e)}")


@router.put("/admin/teachers/{teacher_id}", response_model=UserResponse)
def update_teacher_admin(
    teacher_id: str,
    teacher_data: TeacherUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a teacher account (admin only)"""
    try:
        # Check if current user is admin
        role_value = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
        if role_value != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can update teacher accounts"
            )
        
        # Get teacher user
        teacher = db.query(User).filter(User.id == teacher_id, User.role == "teacher").first()
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")
        
        # Update allowed fields
        if teacher_data.name is not None:
            teacher.name = teacher_data.name
        if teacher_data.email is not None:
            # Check if new email is already in use
            existing = db.query(User).filter(
                User.email == teacher_data.email,
                User.id != teacher_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
            teacher.email = teacher_data.email
        if teacher_data.password is not None:
            teacher.password_hash = get_password_hash(teacher_data.password)
        
        db.commit()
        db.refresh(teacher)
        
        print(f"[INFO] Teacher account updated by admin: {teacher.email} (ID: {teacher.id})")
        return teacher
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to update teacher: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update teacher: {str(e)}")


@router.delete("/admin/teachers/{teacher_id}")
def delete_teacher_admin(
    teacher_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a teacher account (admin only)"""
    try:
        # Check if current user is admin
        role_value = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
        if role_value != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can delete teacher accounts"
            )
        
        # Get teacher user
        teacher = db.query(User).filter(User.id == teacher_id, User.role == "teacher").first()
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")
        
        # Delete teacher profile and related data
        teacher_profile = db.query(Teacher).filter(Teacher.user_id == teacher_id).first()
        if teacher_profile:
            # Delete time slots
            db.query(TimeSlot).filter(TimeSlot.teacher_id == teacher_profile.id).delete()
            # Delete teacher profile
            db.delete(teacher_profile)
        
        # Delete user
        db.delete(teacher)
        db.commit()
        
        print(f"[INFO] Teacher account deleted by admin: {teacher.email} (ID: {teacher.id})")
        return {"message": f"Teacher {teacher.email} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to delete teacher: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete teacher: {str(e)}")
