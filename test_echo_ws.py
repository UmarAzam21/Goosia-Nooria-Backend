"""
Test the simple echo WebSocket endpoint
"""
import asyncio
import websockets

async def test_echo():
    try:
        async with websockets.connect("ws://localhost:5000/ws/echo") as ws:
            print("✅ Connected!")
            msg = await asyncio.wait_for(ws.recv(), timeout=5)
            print(f"Received: {msg}")
            
            await ws.send("Test message")
            echo = await asyncio.wait_for(ws.recv(), timeout=5)
            print(f"Echo: {echo}")
            print("✅ SUCCESS!")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_echo())
