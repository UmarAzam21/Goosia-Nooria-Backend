"""
Direct WebSocket test - manually connect and send messages to test the chat flow
"""
import asyncio
import websockets
import json
import sys
from datetime import datetime

async def test_websocket():
    # Test parameters
    STUDENT_ID = 5
    ADMIN_ID = 1
    WS_URL = f"ws://localhost:5000/ws/chat/{STUDENT_ID}/{ADMIN_ID}"
    
    print("\n" + "="*80)
    print("WEBSOCKET DIRECT TEST")
    print("="*80)
    print(f"\nConnecting to: {WS_URL}")
    print(f"Student ID: {STUDENT_ID}, Admin ID: {ADMIN_ID}\n")
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("✅ Connected to WebSocket\n")
            
            # Receive initial history
            print("📨 Waiting for initial message from server...")
            message = await asyncio.wait_for(websocket.recv(), timeout=5)
            data = json.loads(message)
            print(f"📚 Received {len(data.get('messages', []))} messages from history\n")
            
            # Send test message
            print("📤 Sending test message...")
            test_msg = {
                "type": "message",
                "text": f"Test message at {datetime.now().strftime('%H:%M:%S')}",
                "sender_id": STUDENT_ID,
                "sender_role": "student"
            }
            
            await websocket.send(json.dumps(test_msg))
            print(f"✅ Sent: {test_msg['text']}\n")
            
            # Wait for response
            print("📨 Waiting for message broadcast back...")
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            response_data = json.loads(response)
            
            print(f"📬 Received broadcast response:")
            print(f"   ID: {response_data.get('id')}")
            print(f"   Sender: {response_data.get('sender_name')} ({response_data.get('sender_role')})")
            print(f"   Text: {response_data.get('text')}")
            print(f"   Created: {response_data.get('created_at')}\n")
            
            # Wait a bit and disconnect
            await asyncio.sleep(1)
            
    except asyncio.TimeoutError:
        print("❌ Timeout waiting for message")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("✅ Test completed successfully")

if __name__ == "__main__":
    asyncio.run(test_websocket())
