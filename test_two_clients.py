#!/usr/bin/env python3
"""Test real-time chat with two connected clients"""
import asyncio
import websockets
import json
import time

async def send_messages(client_name, sender_id, receiver_name):
    try:
        admin_id = 1 if sender_id == 5 else 5
        ws_url = f"ws://localhost:5001/ws/chat/{min(sender_id, admin_id)}/{max(sender_id, admin_id)}"
        
        print(f"\n[{client_name}] Connecting to {ws_url}")
        async with websockets.connect(ws_url) as ws:
            # Receive history
            history = await asyncio.wait_for(ws.recv(), timeout=2)
            data = json.loads(history)
            print(f"[{client_name}] Received history: {len(data.get('messages', []))} messages")
            
            # Send message 1
            msg1_text = f"Message 1 from {client_name}"
            print(f"[{client_name}] Sending: '{msg1_text}'")
            await ws.send(json.dumps({
                "type": "message",
                "text": msg1_text,
                "sender_id": sender_id
            }))
            
            # Receive broadcast
            response1 = await asyncio.wait_for(ws.recv(), timeout=2)
            data1 = json.loads(response1)
            if data1.get('type') == 'message':
                print(f"[{client_name}] ✅ Confirmed Message 1: ID={data1.get('id')}, Text='{data1.get('text')}'")
            
            await asyncio.sleep(0.3)
            
            # Send message 2
            msg2_text = f"Message 2 from {client_name}"
            print(f"[{client_name}] Sending: '{msg2_text}'")
            await ws.send(json.dumps({
                "type": "message",
                "text": msg2_text,
                "sender_id": sender_id
            }))
            
            # Receive broadcast
            response2 = await asyncio.wait_for(ws.recv(), timeout=2)
            data2 = json.loads(response2)
            if data2.get('type') == 'message':
                print(f"[{client_name}] ✅ Confirmed Message 2: ID={data2.get('id')}, Text='{data2.get('text')}'")
            
            # Wait and listen for any other messages
            try:
                while True:
                    msg = await asyncio.wait_for(ws.recv(), timeout=1)
                    data = json.loads(msg)
                    if data.get('type') == 'message':
                        print(f"[{client_name}] 📨 Received: ID={data.get('id')}, Text='{data.get('text')}'")
            except asyncio.TimeoutError:
                pass
                
    except Exception as e:
        print(f"[{client_name}] ❌ ERROR: {e}")

async def main():
    print("=" * 80)
    print("TESTING TWO-CLIENT CHAT")
    print("=" * 80)
    
    # Run both clients concurrently
    await asyncio.gather(
        send_messages("STUDENT (ID=5)", 5, "Admin"),
        send_messages("ADMIN (ID=1)", 1, "Student")
    )
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE - Check if both clients received all messages")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
