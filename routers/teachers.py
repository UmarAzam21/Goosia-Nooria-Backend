from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Teacher, TimeSlot, User
from schemas import (
    TeacherCreate,
    TeacherResponse,
    TimeSlotCreate,
    TimeSlotResponse
)

router = APIRouter()

@router.get("/", response_model=List[TeacherResponse])
def get_all_teachers(
    course_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all available teachers (course_id parameter is ignored to show all teachers)"""
    query = db.query(Teacher).join(User, Teacher.user_id == User.id).filter(
        Teacher.is_available == True
    )
    
    # Show all available teachers regardless of course_id
    # This allows students to choose from any available teacher for any course
    teachers = query.offset(skip).limit(limit).all()
    print(f"[INFO] Retrieved {len(teachers)} available teachers (course_id filter ignored to show all)")
    return teachers

@router.get("/{teacher_id}", response_model=TeacherResponse)
def get_teacher(teacher_id: int, db: Session = Depends(get_db)):
    """Get a specific teacher by ID"""
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher

@router.get("/{teacher_id}/time-slots", response_model=List[TimeSlotResponse])
def get_teacher_time_slots(teacher_id: int, db: Session = Depends(get_db)):
    """Get all time slots for a specific teacher"""
    time_slots = db.query(TimeSlot).filter(
        TimeSlot.teacher_id == teacher_id,
        TimeSlot.is_available == True
    ).all()
    print(f"[INFO] Retrieved {len(time_slots)} available time slots for teacher ID {teacher_id}")
    return time_slots

@router.post("/", response_model=TeacherResponse, status_code=status.HTTP_201_CREATED)
def create_teacher(
    teacher: TeacherCreate,
    db: Session = Depends(get_db)
):
    """Create a new teacher profile"""
    # Check if user exists
    user = db.query(User).filter(User.id == teacher.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if teacher profile already exists
    existing_teacher = db.query(Teacher).filter(Teacher.user_id == teacher.user_id).first()
    if existing_teacher:
        raise HTTPException(status_code=400, detail="Teacher profile already exists")
    
    db_teacher = Teacher(**teacher.dict())
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher

@router.post("/{teacher_id}/time-slots", response_model=TimeSlotResponse, status_code=status.HTTP_201_CREATED)
def create_time_slot(
    teacher_id: int,
    time_slot: TimeSlotCreate,
    db: Session = Depends(get_db)
):
    """Create a new time slot for a teacher"""
    # Verify teacher exists
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    time_slot_data = time_slot.dict()
    time_slot_data['teacher_id'] = teacher_id
    
    db_time_slot = TimeSlot(**time_slot_data)
    db.add(db_time_slot)
    db.commit()
    db.refresh(db_time_slot)
    return db_time_slot
