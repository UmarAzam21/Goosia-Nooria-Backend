#!/usr/bin/env python3
"""Test real-time chat with multiple messages"""
import asyncio
import websockets
import json
import time

async def test_multiple_messages():
    try:
        print("=" * 80)
        print("TESTING MULTIPLE MESSAGES IN CHAT")
        print("=" * 80)
        
        async with websockets.connect('ws://localhost:5001/ws/chat/5/1') as ws:
            print("\n✅ Connected to WebSocket\n")
            
            # Receive history
            history = await asyncio.wait_for(ws.recv(), timeout=2)
            data = json.loads(history)
            print(f"📚 Received History: {len(data.get('messages', []))} messages")
            for msg in data.get('messages', []):
                print(f"   - ID: {msg['id']}, Text: {msg['text']}, Sender: {msg['sender_id']}")
            
            # Send first message
            print("\n📤 Sending Message 1: 'i am fine'")
            msg1 = {
                "type": "message",
                "text": "i am fine",
                "sender_id": 5
            }
            await ws.send(json.dumps(msg1))
            
            # Receive broadcast with ID
            response1 = await asyncio.wait_for(ws.recv(), timeout=2)
            data1 = json.loads(response1)
            print(f"📨 Response 1: ID={data1.get('id')}, Text='{data1.get('text')}'")
            
            time.sleep(0.5)
            
            # Send second message
            print("\n📤 Sending Message 2: 'how are you'")
            msg2 = {
                "type": "message",
                "text": "how are you",
                "sender_id": 5
            }
            await ws.send(json.dumps(msg2))
            
            # Receive broadcast with ID
            response2 = await asyncio.wait_for(ws.recv(), timeout=2)
            data2 = json.loads(response2)
            print(f"📨 Response 2: ID={data2.get('id')}, Text='{data2.get('text')}'")
            
            print("\n" + "=" * 80)
            print("✅ TEST RESULTS:")
            print(f"   Message 1: ID={data1.get('id')}, Text='{data1.get('text')}'")
            print(f"   Message 2: ID={data2.get('id')}, Text='{data2.get('text')}'")
            print(f"   IDs are different: {data1.get('id') != data2.get('id')}")
            print("=" * 80)
            
    except asyncio.TimeoutError:
        print("❌ Timeout waiting for response")
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_multiple_messages())
