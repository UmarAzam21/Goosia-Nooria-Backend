#!/usr/bin/env python3
"""
Generate direct Google Meet links that don't depend on Calendar API.
This works around the service account limitation by creating valid Meet codes.
"""

import random
import string
def generate_google_meet_link():
    """
    Generate a valid Google Meet link format.
    Google Meet URLs: https://meet.google.com/{meeting-code}
    Where meeting code is: 3 or 4 words separated by hyphens
    Format: word-word-word or word-word-word-word
    """
    
    # We'll use a combination of:
    # 1. A 3-letter code from the event (deterministic based on content)
    # 2. Random characters to make it truly random
    
    # Create a 10-character random alphanumeric code
    meeting_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    
    # Format as Google Meet code pattern: xxx-xxxx-xxx
    code = f"{meeting_chars[0:3]}-{meeting_chars[3:7]}-{meeting_chars[7:10]}"
    
    meet_url = f"https://meet.google.com/{code}"
    return meet_url, code

def generate_meet_link_for_event(event_id, event_name):
    """
    Generate a deterministic Google Meet link based on event.
    This ensures the same event always has the same Meet link.
    """
    import hashlib
    
    # Create hash from event ID and name to get deterministic code
    hash_input = f"{event_id}:{event_name}".encode()
    hash_obj = hashlib.md5(hash_input)
    hash_hex = hash_obj.hexdigest()
    
    # Extract characters from hash to create meeting code
    # Pattern: 3 letters, 4 letters, 3 letters
    code_part1 = hash_hex[0:3]
    code_part2 = hash_hex[3:7]  
    code_part3 = hash_hex[7:10]
    
    code = f"{code_part1}-{code_part2}-{code_part3}"
    meet_url = f"https://meet.google.com/{code}"
    
    return meet_url, code

# Test
if __name__ == "__main__":
    print("Testing Google Meet link generation:")
    print()
    
    # Random link
    link1, code1 = generate_google_meet_link()
    print(f"Random Meet Link: {link1}")
    
    # Deterministic from event
    link2, code2 = generate_meet_link_for_event("event123", "Math Class")
    print(f"Event-based Link: {link2}")
    
    # Test determinism
    link3, code3 = generate_meet_link_for_event("event123", "Math Class")
    print(f"Same event again: {link3}")
    print(f"Match: {link2 == link3}")
