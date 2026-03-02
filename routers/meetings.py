from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

from database import get_db
from models import User, Class
from auth import get_current_user
from google_meet_service import create_meet_event, get_event_details, delete_event, update_event

router = APIRouter()


class MeetingCreate(BaseModel):
    class_id: int
    meeting_name: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    description: Optional[str] = None


class MeetingUpdateRequest(BaseModel):
    meeting_name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    description: Optional[str] = None


class MeetingResponse(BaseModel):
    success: bool
    event_id: Optional[str] = None
    join_url: Optional[str] = None
    message: Optional[str] = None


@router.post("/meetings/create", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
def create_class_meeting(
    meeting_data: MeetingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new Google Meet event for a class
    Only teachers can create meetings for their classes
    """
    # Get the class
    class_obj = db.query(Class).filter(Class.id == meeting_data.class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Check if user is the teacher
    if class_obj.enrollment.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the class teacher can create meetings")
    
    # Set default times if not provided
    start_time = meeting_data.start_time or datetime.now() + timedelta(hours=1)
    end_time = meeting_data.end_time or (start_time + timedelta(hours=1))
    
    # Create the Google Meet event
    result = create_meet_event(
        event_name=meeting_data.meeting_name,
        start_time=start_time,
        end_time=end_time,
        description=meeting_data.description or f"Online class: {meeting_data.meeting_name}"
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create Google Meet event: {result.get('error', 'Unknown error')}"
        )
    
    event_id = result.get("event_id")
    calendar_link = result.get("calendar_url")
    
    return MeetingResponse(
        success=True,
        event_id=event_id,
        join_url=calendar_link,
        message="Google Calendar event with Meet created successfully"
    )


@router.post("/meetings/join", response_model=MeetingResponse)
def join_meeting(
    event_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get Google Meet join URL for an event
    """
    try:
        event_info = get_event_details(event_id)
        
        if not event_info["success"]:
            raise HTTPException(status_code=404, detail=f"Event not found: {event_info.get('error')}")
        
        return MeetingResponse(
            success=True,
            event_id=event_id,
            join_url=event_info.get("meet_link"),
            message="Join URL retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get join URL: {str(e)}")


@router.post("/meetings/{event_id}/update", response_model=MeetingResponse)
def update_meeting(
    event_id: str,
    update_data: MeetingUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a Google Meet event
    Only organizer can update
    """
    result = update_event(
        event_id=event_id,
        event_name=update_data.meeting_name,
        start_time=update_data.start_time,
        end_time=update_data.end_time,
        description=update_data.description
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update event: {result.get('error', 'Unknown error')}"
        )
    
    return MeetingResponse(
        success=True,
        event_id=event_id,
        message="Google Meet event updated successfully"
    )


@router.post("/meetings/{event_id}/delete")
def delete_class_meeting(
    event_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a Google Meet event
    Only organizer can delete
    """
    result = delete_event(event_id=event_id)
    
    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete event: {result.get('error', 'Unknown error')}"
        )
    
    return {
        "success": True,
        "message": "Google Meet event deleted successfully",
        "event_id": event_id
    }


@router.get("/meetings/{event_id}/info")
def get_meeting_info(
    event_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get information about a Google Meet event
    """
    try:
        event_info = get_event_details(event_id)
        
        if not event_info["success"]:
            raise HTTPException(status_code=404, detail=f"Failed to get event info: {event_info.get('error')}")
        
        return event_info
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Failed to get event info: {str(e)}"
        )
