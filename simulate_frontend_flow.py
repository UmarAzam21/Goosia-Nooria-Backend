#!/usr/bin/env python3
"""
Simulate the EXACT flow that happens in the browser:
1. Student logs in (gets auth token)
2. Sidebar fetches /my-messages
3. Sidebar calculates unread count
4. Admin sends message
5. Sidebar re-fetches (polling) and should see new unread message
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5001/api"

def log(prefix, msg, data=None):
    """Print colored log messages like the frontend console"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    if data:
        print(f"[{timestamp}] {prefix} {msg}")
        print(f"         → {json.dumps(data, indent=2)}")
    else:
        print(f"[{timestamp}] {prefix} {msg}")

def main():
    print("\n" + "="*80)
    print("FRONTEND FLOW SIMULATION - Badge Display Test")
    print("="*80 + "\n")
    
    # ============================================================
    # PHASE 1: STUDENT LOGS IN
    # ============================================================
    print("📋 PHASE 1: Student Login")
    print("-" * 80)
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login/json",
            json={"email": "ali@student.com", "password": "student123"},
            timeout=5
        )
        
        if response.status_code != 200:
            log("❌", f"Student login failed: {response.status_code}")
            return
        
        student_data = response.json()
        student_token = student_data.get("access_token")
        student_id = student_data.get("user", {}).get("id")
        
        log("✅", f"Student logged in", {
            "user_id": student_id,
            "email": "ali@student.com",
            "token": student_token[:20] + "..."
        })
        
    except Exception as e:
        log("❌", f"Student login error: {str(e)}")
        return
    
    # ============================================================
    # PHASE 2: STUDENT SIDEBAR - FETCH INITIAL UNREAD COUNT
    # ============================================================
    print("\n📋 PHASE 2: Student Sidebar - Initial Fetch")
    print("-" * 80)
    
    headers = {
        "Authorization": f"Bearer {student_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/messages/my-messages",
            headers=headers,
            timeout=5
        )
        
        if response.status_code != 200:
            log("❌", f"Failed to fetch messages: {response.status_code}")
            log("   ", f"Response: {response.text}")
            return
        
        messages_before = response.json()
        log("✅", f"Student fetched messages", {
            "total_messages": len(messages_before),
            "unread_count_before": sum(1 for m in messages_before if m.get("sender_id") != student_id and not m.get("is_read"))
        })
        
        # Show existing messages
        if messages_before:
            log("📥", f"Existing messages from server:")
            for msg in messages_before:
                is_from_admin = msg.get("sender_id") != student_id
                unread = not msg.get("is_read")
                status = "📖 READ" if not unread else "📕 UNREAD"
                log("   ", f"[ID:{msg.get('id')}] {status} - {msg.get('message', '')[:40]}", {
                    "sender_id": msg.get("sender_id"),
                    "is_read": msg.get("is_read"),
                    "from_admin": is_from_admin
                })
        
    except Exception as e:
        log("❌", f"Fetch messages error: {str(e)}")
        return
    
    # ============================================================
    # PHASE 3: ADMIN LOGS IN AND SENDS MESSAGE
    # ============================================================
    print("\n📋 PHASE 3: Admin Login & Send Message")
    print("-" * 80)
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login/json",
            json={"email": "admin@masjid.com", "password": "admin123"},
            timeout=5
        )
        
        if response.status_code != 200:
            log("❌", f"Admin login failed: {response.status_code}")
            return
        
        admin_data = response.json()
        admin_token = admin_data.get("access_token")
        admin_id = admin_data.get("user", {}).get("id")
        
        log("✅", f"Admin logged in", {
            "user_id": admin_id,
            "email": "admin@masjid.com",
            "token": admin_token[:20] + "..."
        })
        
    except Exception as e:
        log("❌", f"Admin login error: {str(e)}")
        return
    
    # Admin sends message to student
    print()
    try:
        test_message = f"Test message from admin - {int(time.time())}"
        
        response = requests.post(
            f"{BASE_URL}/messages/admin/send-to-student",
            json={
                "student_id": student_id,
                "message": test_message
            },
            headers={
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            },
            timeout=5
        )
        
        if response.status_code != 200:
            log("❌", f"Message send failed: {response.status_code}")
            log("   ", f"Response: {response.text}")
            return
        
        sent_msg = response.json()
        log("✅", f"Admin sent message to student", {
            "message_id": sent_msg.get("id"),
            "student_id": student_id,
            "message": test_message,
            "is_read_in_response": sent_msg.get("is_read")
        })
        
    except Exception as e:
        log("❌", f"Send message error: {str(e)}")
        return
    
    # ============================================================
    # PHASE 4: STUDENT SIDEBAR - POLLING AFTER MESSAGE SENT
    # ============================================================
    print("\n📋 PHASE 4: Student Sidebar - Polling (Simulating real-time)")
    print("-" * 80)
    
    time.sleep(1)  # Simulate delay, then sidebar polling interval
    
    try:
        response = requests.get(
            f"{BASE_URL}/messages/my-messages",
            headers=headers,
            timeout=5
        )
        
        if response.status_code != 200:
            log("❌", f"Failed to fetch messages after send: {response.status_code}")
            return
        
        messages_after = response.json()
        log("✅", f"Student fetched messages (after admin sent)", {
            "total_messages": len(messages_after),
            "messages_added": len(messages_after) - len(messages_before)
        })
        
    except Exception as e:
        log("❌", f"Fetch messages error: {str(e)}")
        return
    
    # ============================================================
    # PHASE 5: CALCULATE BADGE COUNT (Frontend Logic)
    # ============================================================
    print("\n📋 PHASE 5: Frontend Badge Calculation")
    print("-" * 80)
    
    # This is the EXACT logic from layout.js
    unread_from_admin = [
        msg for msg in messages_after 
        if msg.get("sender_id") != student_id and not msg.get("is_read")
    ]
    
    badge_count = len(unread_from_admin)
    
    log("🔵", f"Frontend filtering logic:", {
        "condition": f"sender_id != {student_id} AND !is_read",
        "total_messages": len(messages_after),
        "matches_condition": len(unread_from_admin)
    })
    
    # Show each message and why it was/wasn't included
    print()
    for msg in messages_after[-5:]:  # Show last 5 messages
        sender_id = msg.get("sender_id")
        is_read = msg.get("is_read")
        
        matches = (sender_id != student_id) and (not is_read)
        
        symbol = "✅" if matches else "❌"
        from_who = "ADMIN" if sender_id != student_id else "STUDENT"
        read_status = "READ" if is_read else "UNREAD"
        
        log("   ", f"{symbol} [{from_who}] {read_status} - {msg.get('message', '')[:40]}", {
            "id": msg.get("id"),
            "sender_id": sender_id,
            "is_read": is_read,
            "included_in_badge": matches
        })
    
    # ============================================================
    # FINAL RESULT
    # ============================================================
    print("\n" + "="*80)
    print("FINAL RESULT")
    print("="*80)
    
    if badge_count > 0:
        print(f"\n✅ SUCCESS: Badge SHOULD display: {badge_count} unread message(s)")
        print(f"\n   The sidebar 'My Messages' link should show a red badge with number: {badge_count}")
        print(f"\n   In React state: unreadCount = {badge_count}")
        print(f"   Badge render: {{hasUnread && <span>{{unreadCount}}</span>}}")
        print(f"   hasUnread = (item.name === 'My Messages' && {badge_count} > 0) = TRUE")
    else:
        print(f"\n❌ ERROR: Badge will NOT display")
        print(f"\n   unreadCount = 0")
        print(f"   No messages from admin with is_read=false found")
        print(f"\n   Check database:")
        print(f"   - Last message sender_id should be {admin_id} (admin's ID)")
        print(f"   - Last message is_read should be FALSE")
    
    print("\n" + "-"*80)
    print("DEBUG INFO:")
    print("-"*80)
    print(f"Student ID: {student_id}")
    print(f"Admin ID: {admin_id}")
    print(f"Total messages after: {len(messages_after)}")
    print(f"Last message info:")
    if messages_after:
        last = messages_after[-1]
        print(f"  - ID: {last.get('id')}")
        print(f"  - sender_id: {last.get('sender_id')}")
        print(f"  - is_read: {last.get('is_read')}")
        print(f"  - message: {last.get('message')}")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
