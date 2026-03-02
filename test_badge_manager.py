#!/usr/bin/env python3
"""
Badge Manager Test Script
Demonstrates badge system functionality
"""

from badge_manager import badge_manager, UserChatState

print("=" * 70)
print("TEST: Badge Manager System")
print("=" * 70)

# Test 1: Initial state
print("\n[TEST 1] Initial State")
print("-" * 70)
user_id = 5
state = badge_manager.get_user_state(user_id)
print(f"User {user_id} initial state:")
print(f"  is_chat_open: {state['is_chat_open']}")
print(f"  unread_count: {state['unread_count']}")
assert not state['is_chat_open'], "Chat should be closed initially"
assert state['unread_count'] == 0, "Unread count should be 0 initially"
print("✅ PASS")

# Test 2: Message received while chat is closed
print("\n[TEST 2] Message While Chat Closed")
print("-" * 70)
badge_manager.close_chat(user_id)
event = badge_manager.receive_message(user_id)
print(f"Event returned: {event}")
assert event is not None, "Should return event when chat is closed"
assert event['event'] == 'BADGE_COUNT', "Should be BADGE_COUNT event"
assert event['count'] == 1, "Count should be 1"
print("✅ PASS")

# Test 3: Multiple messages while closed
print("\n[TEST 3] Multiple Messages While Closed")
print("-" * 70)
event2 = badge_manager.receive_message(user_id)
event3 = badge_manager.receive_message(user_id)
print(f"Message 2 event: {event2}")
print(f"Message 3 event: {event3}")
assert event2['count'] == 2, "Count should be 2"
assert event3['count'] == 3, "Count should be 3"
state = badge_manager.get_user_state(user_id)
print(f"Current unread_count: {state['unread_count']}")
assert state['unread_count'] == 3, "Total unread should be 3"
print("✅ PASS")

# Test 4: Open chat - count resets
print("\n[TEST 4] Chat Opened - Count Resets")
print("-" * 70)
event = badge_manager.open_chat(user_id)
print(f"Event returned: {event}")
assert event['event'] == 'BADGE_COUNT', "Should be BADGE_COUNT"
assert event['count'] == 0, "Count should reset to 0"
state = badge_manager.get_user_state(user_id)
print(f"is_chat_open: {state['is_chat_open']}")
print(f"unread_count: {state['unread_count']}")
assert state['is_chat_open'], "Chat should be open"
assert state['unread_count'] == 0, "Unread should be 0"
print("✅ PASS")

# Test 5: Message while chat is open - no increment
print("\n[TEST 5] Message While Chat Open - No Increment")
print("-" * 70)
event = badge_manager.receive_message(user_id)
print(f"Event returned: {event}")
assert event is None, "Should return None when chat is open"
state = badge_manager.get_user_state(user_id)
print(f"unread_count: {state['unread_count']}")
assert state['unread_count'] == 0, "Count should NOT increment when chat is open"
print("✅ PASS")

# Test 6: Close chat - ready to track again
print("\n[TEST 6] Chat Closed - Ready to Track Again")
print("-" * 70)
event = badge_manager.close_chat(user_id)
print(f"Event returned: {event}")
assert event['event'] == 'CHAT_CLOSED', "Should return CHAT_CLOSED"
state = badge_manager.get_user_state(user_id)
print(f"is_chat_open: {state['is_chat_open']}")
assert not state['is_chat_open'], "Chat should be closed"
print("✅ PASS")

# Test 7: Message after closing - count increases
print("\n[TEST 7] Message After Closing - Count Increases")
print("-" * 70)
event = badge_manager.receive_message(user_id)
print(f"Event returned: {event}")
assert event is not None, "Should return event"
assert event['count'] == 1, "Count should be 1 (reset after opening)"
state = badge_manager.get_user_state(user_id)
print(f"unread_count: {state['unread_count']}")
assert state['unread_count'] == 1, "Count should be 1"
print("✅ PASS")

# Test 8: Multiple users work independently
print("\n[TEST 8] Multiple Users Work Independently")
print("-" * 70)
user_id_2 = 10
badge_manager.close_chat(user_id_2)
event1 = badge_manager.receive_message(user_id_2)
event2 = badge_manager.receive_message(user_id_2)
state1 = badge_manager.get_user_state(user_id)
state2 = badge_manager.get_user_state(user_id_2)
print(f"User {user_id}: unread_count={state1['unread_count']}")
print(f"User {user_id_2}: unread_count={state2['unread_count']}")
assert state1['unread_count'] == 1, "User 5 should have 1 unread"
assert state2['unread_count'] == 2, "User 10 should have 2 unread"
print("✅ PASS")

# Test 9: Reset count
print("\n[TEST 9] Reset Unread Count")
print("-" * 70)
event = badge_manager.reset_count(user_id_2)
print(f"Event returned: {event}")
assert event['event'] == 'BADGE_COUNT', "Should be BADGE_COUNT"
assert event['count'] == 0, "Count should be 0"
state = badge_manager.get_user_state(user_id_2)
print(f"User {user_id_2} unread_count after reset: {state['unread_count']}")
assert state['unread_count'] == 0, "Should be reset to 0"
print("✅ PASS")

# Test 10: Get methods work correctly
print("\n[TEST 10] Get Methods")
print("-" * 70)
badge_manager.open_chat(user_id)
count = badge_manager.get_unread_count(user_id)
is_open = badge_manager.get_chat_open_status(user_id)
print(f"get_unread_count({user_id}): {count}")
print(f"get_chat_open_status({user_id}): {is_open}")
assert count == 1, "Unread count should be 1"
assert is_open, "Chat should be open"
print("✅ PASS")

print("\n" + "=" * 70)
print("ALL TESTS PASSED! ✅")
print("=" * 70)
print("\nBadge Manager is working correctly!")
print("Ready for WebSocket integration.")
