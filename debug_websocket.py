"""
Debug WebSocket handshake by checking response headers
"""
import asyncio
import websockets

async def debug_websocket():
    WS_URL = "ws://localhost:5000/ws/test"
    
    print(f"\nAttempting connection to: {WS_URL}")
    print("=" * 60)
    
    try:
        # Try to connect and capture the error
        async with websockets.connect(WS_URL, close_timeout=5) as websocket:
            print("✅ Connected!")
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ InvalidStatusCode: {e.status_code}")
        print(f"Status Code: {e.status_code}")
        print(f"Response Headers: {e.response_headers}")
        print(f"\n" + "=" * 60)
        print("HEADERS RECEIVED:")
        for key, value in e.response_headers.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_websocket())
