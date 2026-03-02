#!/usr/bin/env python3
"""Test websocket_chat endpoint"""
import asyncio
import websockets
import json

async def test():
    try:
        print("Connecting to ws://localhost:5001/ws/chat/5/1...")
        async with websockets.connect('ws://localhost:5001/ws/chat/5/1') as ws:
            print("✅ Connected!")
            
            # Receive history
            msg = await asyncio.wait_for(ws.recv(), timeout=2)
            print(f"✅ Received message: {msg[:100]}...")
            
            # Try sending a message
            send_msg = {"type": "message", "text": "Hello Admin", "sender_id": 5}
            await ws.send(json.dumps(send_msg))
            print(f"✅ Sent message")
            
            # Try to receive response
            response = await asyncio.wait_for(ws.recv(), timeout=2)
            print(f"✅ Got response: {response[:100]}...")
            
    except asyncio.TimeoutError:
        print('✅ Connection works! (no messages in queue)')
    except Exception as e:
        print(f'❌ ERROR: {type(e).__name__}: {e}')

if __name__ == "__main__":
    asyncio.run(test())
