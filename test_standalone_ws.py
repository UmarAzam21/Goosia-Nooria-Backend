#!/usr/bin/env python3
"""Completely standalone WebSocket server for testing"""
import asyncio
from fastapi import FastAPI, WebSocket
import uvicorn

app = FastAPI()

@app.websocket("/ws/test")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("Hello from standalone server!")
    await websocket.close()

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    print("Starting standalone WebSocket server on port 8888...")
    uvicorn.run(app, host="127.0.0.1", port=8888, reload=False)
