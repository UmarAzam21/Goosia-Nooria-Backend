"""
Test the simple WebSocket endpoint
"""
import asyncio
import websockets
import json
import sys

async def test_simple_websocket():
    WS_URL = "ws://localhost:5000/ws/test"
    
    print("\n" + "="*80)
    print("SIMPLE WEBSOCKET TEST")
    print("="*80)
    print(f"\nConnecting to: {WS_URL}\n")
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("✅ Connected to test WebSocket\n")
            
            # Receive initial message
            message = await asyncio.wait_for(websocket.recv(), timeout=5)
            data = json.loads(message)
            print(f"📨 Received from server: {data}\n")
            
            # Send a message
            await websocket.send("Hello from client!")
            print("📤 Sent: Hello from client!\n")
            
            # Receive echo
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            response_data = json.loads(response)
            print(f"📬 Received echo: {response_data}\n")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("✅ Simple WebSocket test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_simple_websocket())
