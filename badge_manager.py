"""
Unread Message Badge Manager
Tracks per-user chat open/closed state and unread message count
"""

from typing import Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class UserChatState:
    """Per-user chat state for badge tracking"""
    user_id: int
    is_chat_open: bool = False  # Is the chat tab open?
    unread_count: int = 0  # Number of unread messages
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for sending over WebSocket"""
        return {
            "user_id": self.user_id,
            "is_chat_open": self.is_chat_open,
            "unread_count": self.unread_count,
            "last_updated": self.last_updated.isoformat()
        }


class BadgeManager:
    """
    Tracks unread message badge state for all users.
    
    Per-user tracking:
    - is_chat_open: boolean (True if user has chat tab open)
    - unread_count: integer (number of messages while chat was closed)
    
    When message arrives:
    - If is_chat_open=False → increment unread_count, emit BADGE_COUNT event
    - If is_chat_open=True → don't increment (user is reading in real-time)
    
    When CHAT_OPEN event:
    - Set is_chat_open=True
    - Reset unread_count=0
    - Emit BADGE_COUNT with count=0
    
    When CHAT_CLOSE event:
    - Set is_chat_open=False
    """
    
    def __init__(self):
        # user_id → UserChatState
        self.user_states: Dict[int, UserChatState] = {}
    
    def get_or_create_user(self, user_id: int) -> UserChatState:
        """Get user state, create if doesn't exist"""
        if user_id not in self.user_states:
            self.user_states[user_id] = UserChatState(user_id=user_id)
        return self.user_states[user_id]
    
    def open_chat(self, user_id: int) -> dict:
        """
        User opened the chat tab.
        
        Returns: {"event": "BADGE_COUNT", "user_id": X, "count": 0}
        """
        user_state = self.get_or_create_user(user_id)
        user_state.is_chat_open = True
        user_state.unread_count = 0
        user_state.last_updated = datetime.now()
        
        print(f"[BADGE] User {user_id} OPENED chat tab → unread_count=0")
        
        return {
            "event": "BADGE_COUNT",
            "user_id": user_id,
            "count": 0
        }
    
    def close_chat(self, user_id: int) -> dict:
        """
        User closed the chat tab.
        Returns: {"event": "CHAT_CLOSED", "user_id": X}
        """
        user_state = self.get_or_create_user(user_id)
        user_state.is_chat_open = False
        user_state.last_updated = datetime.now()
        
        print(f"[BADGE] User {user_id} CLOSED chat tab → ready to track unread")
        
        return {
            "event": "CHAT_CLOSED",
            "user_id": user_id
        }
    
    def receive_message(self, user_id: int) -> Optional[dict]:
        """
        Message arrived for this user.
        
        If user's chat is open → return None (don't increment)
        If user's chat is closed → increment unread and return BADGE_COUNT event
        
        Returns: {"event": "BADGE_COUNT", "user_id": X, "count": N} or None
        """
        user_state = self.get_or_create_user(user_id)
        
        # If chat is open, don't increment (user is reading in real-time)
        if user_state.is_chat_open:
            print(f"[BADGE] User {user_id} chat is OPEN → unread_count NOT incremented")
            return None
        
        # Chat is closed, increment unread count
        user_state.unread_count += 1
        user_state.last_updated = datetime.now()
        
        print(f"[BADGE] User {user_id} chat is CLOSED → unread_count={user_state.unread_count}")
        
        return {
            "event": "BADGE_COUNT",
            "user_id": user_id,
            "count": user_state.unread_count
        }
    
    def get_unread_count(self, user_id: int) -> int:
        """Get current unread count for user"""
        user_state = self.get_or_create_user(user_id)
        return user_state.unread_count
    
    def get_chat_open_status(self, user_id: int) -> bool:
        """Check if user's chat is open"""
        user_state = self.get_or_create_user(user_id)
        return user_state.is_chat_open
    
    def get_user_state(self, user_id: int) -> dict:
        """Get full state of user"""
        user_state = self.get_or_create_user(user_id)
        return user_state.to_dict()
    
    def reset_count(self, user_id: int) -> dict:
        """Reset unread count (when user reads all messages)"""
        user_state = self.get_or_create_user(user_id)
        old_count = user_state.unread_count
        user_state.unread_count = 0
        user_state.last_updated = datetime.now()
        
        print(f"[BADGE] User {user_id} unread count RESET: {old_count} → 0")
        
        return {
            "event": "BADGE_COUNT",
            "user_id": user_id,
            "count": 0
        }


# Global instance
badge_manager = BadgeManager()
