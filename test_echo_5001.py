"""
Test the minimal app on port 5001
"""
import asyncio
import websockets

async def test():
    try:
        async with websockets.connect("ws://localhost:5001/ws/echo") as ws:
            print("✅ Connected!")
            msg = await asyncio.wait_for(ws.recv(), timeout=5)
            print(f"Received: {msg}")
            await ws.send("Test")
            echo = await asyncio.wait_for(ws.recv(), timeout=5)
            print(f"Echo: {echo}")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test())
