"""
Simple WebSocket test endpoint - no dependencies
"""
from fastapi import APIRouter, WebSocket
import sys, traceback

router = APIRouter()

@router.websocket("/ws/test")
async def websocket_test_endpoint(websocket: WebSocket):
    print("🔗 TEST WEBSOCKET: Connection attempt received", flush=True)
    sys.stdout.flush()
    try:
        print("📝 About to accept WebSocket...", flush=True)
        sys.stdout.flush()
        await websocket.accept()
        print("✅ TEST WEBSOCKET: Connection accepted", flush=True)
        sys.stdout.flush()
        
        # Send a test message
        await websocket.send_json({"type": "test", "message": "Hello from WebSocket!"})
        print("📨 TEST WEBSOCKET: Sent test message", flush=True)
        sys.stdout.flush()
        
        # Wait for a message
        while True:
            data = await websocket.receive_text()
            print(f"📬 TEST WEBSOCKET: Received: {data}", flush=True)
            sys.stdout.flush()
            await websocket.send_json({"type": "echo", "message": data})
            
    except Exception as e:
        print(f"❌ TEST WEBSOCKET ERROR: {e}", flush=True)
        traceback.print_exc(file=sys.stdout)
        sys.stdout.flush()
