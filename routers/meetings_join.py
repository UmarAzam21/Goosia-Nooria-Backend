"""
Meeting join routes - handles joining meetings without permission issues
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Class, Enrollment
from auth import get_current_user

router = APIRouter()

@router.get("/join/{event_id}")
def get_join_link(
    event_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get the meeting join link
    Returns a direct Zoom link
    """
    # Look up the enrollment by event ID
    try:
        enrollment_id = int(event_id)
        enrollment = db.query(Enrollment).filter(
            Enrollment.id == enrollment_id
        ).first()
    except (ValueError, TypeError):
        enrollment = None
    
    if not enrollment:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Return the Zoom URL directly
    return {
        "success": True,
        "event_id": event_id,
        "join_url": enrollment.zoom_link,
        "message": "Open the link to join the Zoom meeting"
    }
