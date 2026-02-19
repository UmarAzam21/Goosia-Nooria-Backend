from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from models import Coupon, Course, User, UserRole
from schemas import CouponCreate, CouponResponse
from auth import require_admin

router = APIRouter()

@router.post("/coupons", response_model=CouponResponse, status_code=status.HTTP_201_CREATED)
def create_coupon(
    coupon: CouponCreate,
    course_ids: List[int] = [],
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Create a new coupon/promo code"""
    try:
        # Check if coupon code already exists
        existing = db.query(Coupon).filter(Coupon.code == coupon.code.upper()).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Coupon code already exists"
            )
        
        db_coupon = Coupon(
            code=coupon.code.upper(),
            description=coupon.description,
            discount_type=coupon.discount_type,
            discount_value=coupon.discount_value,
            max_uses=coupon.max_uses,
            is_active=coupon.is_active,
            expires_at=coupon.expires_at,
            created_by=admin.id
        )
        
        # Add courses to coupon if provided
        if course_ids:
            courses = db.query(Course).filter(Course.id.in_(course_ids)).all()
            db_coupon.courses = courses
        
        db.add(db_coupon)
        db.commit()
        db.refresh(db_coupon)
        print(f"[INFO] Coupon created: {db_coupon.code} by admin {admin.email}")
        return db_coupon
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating coupon: {str(e)}"
        )

@router.get("/coupons", response_model=List[CouponResponse])
def get_all_coupons(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Get all coupons"""
    coupons = db.query(Coupon).all()
    return coupons

@router.get("/coupons/{coupon_id}", response_model=CouponResponse)
def get_coupon(
    coupon_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Get coupon details"""
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    return coupon

@router.put("/coupons/{coupon_id}", response_model=CouponResponse)
def update_coupon(
    coupon_id: int,
    coupon_data: CouponCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Update coupon details"""
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    
    coupon.description = coupon_data.description
    coupon.discount_type = coupon_data.discount_type
    coupon.discount_value = coupon_data.discount_value
    coupon.max_uses = coupon_data.max_uses
    coupon.is_active = coupon_data.is_active
    coupon.expires_at = coupon_data.expires_at
    
    db.commit()
    db.refresh(coupon)
    print(f"[INFO] Coupon updated: {coupon.code} by admin {admin.email}")
    return coupon

@router.delete("/coupons/{coupon_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_coupon(
    coupon_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Delete a coupon"""
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    
    db.delete(coupon)
    db.commit()
    print(f"[INFO] Coupon deleted: {coupon.code} by admin {admin.email}")
    return None

@router.post("/coupons/{coupon_id}/apply/{course_id}")
def apply_coupon_to_course(
    coupon_id: int,
    course_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin: Apply coupon to a course"""
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    if course not in coupon.courses:
        coupon.courses.append(course)
        db.commit()
        db.refresh(coupon)
        print(f"[INFO] Coupon {coupon.code} applied to course {course.name} by admin {admin.email}")
    
    return {"message": "Coupon applied to course"}

@router.post("/coupons/validate/{coupon_code}")
def validate_coupon(
    coupon_code: str,
    course_id: int,
    db: Session = Depends(get_db)
):
    """Student: Validate coupon code for a course"""
    coupon = db.query(Coupon).filter(Coupon.code == coupon_code.upper()).first()
    
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon code not found"
        )
    
    # Check if coupon is active
    if not coupon.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon is no longer active"
        )
    
    # Check expiry
    if coupon.expires_at and coupon.expires_at < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon has expired"
        )
    
    # Check usage limit
    if coupon.max_uses and coupon.current_uses >= coupon.max_uses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon usage limit reached"
        )
    
    # Check if coupon applies to this course
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    if course not in coupon.courses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon is not valid for this course"
        )
    
    return {
        "valid": True,
        "discount_type": coupon.discount_type,
        "discount_value": coupon.discount_value,
        "code": coupon.code
    }
