"""
Minimal test app with all routers
"""
from fastapi import FastAPI, WebSocket
from contextlib import asynccontextmanager
import uvicorn

# Database
from database import engine, Base

# Add ALL routers
from routers import auth, courses, teachers, enrollments, classes, payments, chat, dashboard, admin, notifications, coupons, students, groups, meetings, admin_messages, websocket_chat

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

# Add all routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin Management"])
app.include_router(coupons.router, prefix="/api/admin", tags=["Coupons"])
app.include_router(courses.router, prefix="/api/courses", tags=["Courses"])
app.include_router(teachers.router, prefix="/api/teachers", tags=["Teachers"])
app.include_router(enrollments.router, prefix="/api/enrollments", tags=["Enrollments"])
app.include_router(classes.router, prefix="/api/classes", tags=["Classes"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(students.router, prefix="/api/students", tags=["Student Profile"])
app.include_router(groups.router, prefix="/api/groups", tags=["Course Groups"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(notifications.router)
app.include_router(admin_messages.router)
app.include_router(meetings.router, prefix="/api", tags=["Meetings"])
app.include_router(websocket_chat.router, tags=["WebSocket Chat"])

@app.websocket("/ws/echo")
async def websocket_echo(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("Hello!")
    data = await websocket.receive_text()
    await websocket.send_text(f"Echo: {data}")

@app.get("/")
def read_root():
    return {"msg": "OK"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5001)
