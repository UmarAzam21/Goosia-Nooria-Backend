from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, time

from database import get_db
from models import User, Teacher, UserRole, TimeSlot
from schemas import UserCreate, UserLogin, UserResponse, Token
from auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

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
            phone=user.phone,
            country=user.country,
            city=user.city,
            timezone=user.timezone
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # If user is registering as a teacher, create a teacher profile
        if user.role == UserRole.TEACHER or (hasattr(user.role, 'value') and user.role.value == 'teacher') or str(user.role).lower() == 'teacher':
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
            print(f"[INFO] Teacher profile created for user: {db_user.email} (ID: {db_user.id})")
            
            # Create default time slots for the teacher
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
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
            print(f"[INFO] Created {len(time_slots_data)} default time slots for teacher ID {teacher_profile.id}")
        
        print(f"[INFO] User registered successfully: {db_user.email} (ID: {db_user.id})")
        return db_user
    except HTTPException:
        raise
    except Exception as e:
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
