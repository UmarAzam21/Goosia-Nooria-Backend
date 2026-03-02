"""
Test WebSocket on minimal app on port 5001
"""
import asyncio
import websockets
import json
import sys

async def test_minimal_ws():
    WS_URL = "ws://localhost:5001/ws"
    
    print("\nConnecting to minimal WebSocket on port 5001...")
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("✅ Connected!")
            
            # Receive message
            message = await asyncio.wait_for(websocket.recv(), timeout=5)
            print(f"Received: {message}")
            
            # Send message
            await websocket.send("Test message")
            
            # Receive echo
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            print(f"Received echo: {response}")
            
            print("✅ SUCCESS - WebSockets work on minimal app!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_minimal_ws())
