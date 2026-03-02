import hashlib
import requests
from urllib.parse import urlencode
import os
from typing import Optional, Dict, Any
import xml.etree.ElementTree as ET

BBB_SERVER_URL = os.getenv("BBB_SERVER_URL", "https://your-bbb-server.com/bigbluebutton/api")
BBB_SECRET_KEY = os.getenv("BBB_SECRET_KEY", "your-bbb-secret-key")


def generate_checksum(operation: str, params: str = "") -> str:
    """Generate checksum for BigBlueButton API calls"""
    call_string = f"{operation}{params}{BBB_SECRET_KEY}"
    return hashlib.sha1(call_string.encode()).hexdigest()


def create_meeting(
    meeting_name: str,
    meeting_id: str,
    moderator_password: str = "mod123",
    attendee_password: str = "att123",
    welcome_message: str = "",
    logout_url: Optional[str] = None,
    max_participants: int = 100,
    allow_start_stop_recording: bool = True,
    allow_any_user_to_be_moderator: bool = False,
    record: bool = True
) -> Dict[str, Any]:
    """
    Create a new BigBlueButton meeting
    
    Args:
        meeting_name: Name of the meeting
        meeting_id: Unique identifier for the meeting
        moderator_password: Password for moderators
        attendee_password: Password for attendees
        welcome_message: Welcome message to display
        logout_url: URL to redirect after logout
        max_participants: Maximum number of participants
        allow_start_stop_recording: Allow users to start/stop recording
        allow_any_user_to_be_moderator: Allow any user to be moderator
        record: Whether to record the meeting
    
    Returns:
        Dictionary with meeting creation response
    """
    params = {
        "name": meeting_name,
        "meetingID": meeting_id,
        "moderatorPW": moderator_password,
        "attendeePW": attendee_password,
        "allowStartStopRecording": str(allow_start_stop_recording).lower(),
        "record": str(record).lower(),
        "maxParticipants": max_participants,
        "allowAnyUserToBeModeratorAdditionalInfoList": str(allow_any_user_to_be_moderator).lower(),
    }
    
    if welcome_message:
        params["welcome"] = welcome_message
    
    if logout_url:
        params["logoutURL"] = logout_url
    
    params_str = urlencode(params)
    checksum = generate_checksum("create", params_str)
    
    url = f"{BBB_SERVER_URL}/create?{params_str}&checksum={checksum}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        
        result = {
            "success": root.find("returncode").text == "SUCCESS",
            "meeting_id": meeting_id,
            "meeting_name": meeting_name,
        }
        
        if result["success"]:
            result["message"] = root.find("message").text
        else:
            result["message"] = root.find("message").text
            result["error"] = root.find("messageKey").text
        
        return result
    
    except Exception as e:
        return {
            "success": False,
            "meeting_id": meeting_id,
            "error": str(e)
        }


def get_join_url(
    meeting_id: str,
    user_name: str,
    password: str,
    user_id: Optional[str] = None,
    redirect_client_on_exit: bool = True,
    return_url: Optional[str] = None
) -> Optional[str]:
    """
    Generate join URL for a BigBlueButton meeting
    
    Args:
        meeting_id: Meeting ID
        user_name: User's name
        password: Meeting password (moderator or attendee)
        user_id: Optional user ID
        redirect_client_on_exit: Whether to redirect on exit
        return_url: URL to redirect to after logout
    
    Returns:
        Join URL or None if generation fails
    """
    params = {
        "meetingID": meeting_id,
        "fullName": user_name,
        "password": password,
    }
    
    if user_id:
        params["userID"] = user_id
    
    if redirect_client_on_exit:
        params["redirect"] = "true"
    
    if return_url:
        params["redirectClientOnExit"] = return_url
    
    params_str = urlencode(params)
    checksum = generate_checksum("join", params_str)
    
    try:
        return f"{BBB_SERVER_URL}/join?{params_str}&checksum={checksum}"
    except Exception as e:
        print(f"Error generating join URL: {e}")
        return None


def end_meeting(meeting_id: str, password: str) -> Dict[str, Any]:
    """
    End a BigBlueButton meeting
    
    Args:
        meeting_id: Meeting ID
        password: Moderator password
    
    Returns:
        Dictionary with end meeting response
    """
    params = {
        "meetingID": meeting_id,
        "password": password,
    }
    
    params_str = urlencode(params)
    checksum = generate_checksum("end", params_str)
    
    url = f"{BBB_SERVER_URL}/end?{params_str}&checksum={checksum}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        
        return {
            "success": root.find("returncode").text == "SUCCESS",
            "meeting_id": meeting_id,
            "message": root.find("message").text if root.find("message") is not None else "Meeting ended"
        }
    
    except Exception as e:
        return {
            "success": False,
            "meeting_id": meeting_id,
            "error": str(e)
        }


def get_meeting_info(meeting_id: str, password: str) -> Dict[str, Any]:
    """
    Get information about a BigBlueButton meeting
    
    Args:
        meeting_id: Meeting ID
        password: Moderator password
    
    Returns:
        Dictionary with meeting information
    """
    params = {
        "meetingID": meeting_id,
        "password": password,
    }
    
    params_str = urlencode(params)
    checksum = generate_checksum("getMeetingInfo", params_str)
    
    url = f"{BBB_SERVER_URL}/getMeetingInfo?{params_str}&checksum={checksum}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        
        if root.find("returncode").text == "SUCCESS":
            participants = []
            for attendee in root.findall(".//attendee"):
                participants.append({
                    "user_id": attendee.find("userID").text,
                    "name": attendee.find("fullName").text,
                    "role": attendee.find("role").text,
                })
            
            return {
                "success": True,
                "meeting_id": meeting_id,
                "meeting_name": root.find("meetingName").text,
                "is_running": root.find("running").text == "true",
                "participant_count": root.find("participantCount").text,
                "participants": participants,
            }
        else:
            return {
                "success": False,
                "meeting_id": meeting_id,
                "message": root.find("message").text
            }
    
    except Exception as e:
        return {
            "success": False,
            "meeting_id": meeting_id,
            "error": str(e)
        }
