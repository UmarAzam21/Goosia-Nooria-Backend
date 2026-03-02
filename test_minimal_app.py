"""
Minimal test FastAPI app with WebSocket
"""
from fastapi import FastAPI, WebSocket
import uvicorn

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print("🔗 Minimal WebSocket: Connection attempt")
    await websocket.accept()
    print("✅ Minimal WebSocket: Accepted")
    await websocket.send_text("Hello!")
    data = await websocket.receive_text()
    await websocket.send_text(f"Echo: {data}")

@app.get("/")
def read_root():
    return {"message": "Minimal app"}

if __name__ == "__main__":
    print("Starting minimal FastAPI on port 5001...")
    uvicorn.run(app, host="0.0.0.0", port=5001)
