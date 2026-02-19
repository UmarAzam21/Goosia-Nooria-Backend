from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from database import engine, Base
from routers import auth, courses, teachers, enrollments, classes, payments, chat, dashboard, admin, notifications, coupons, students, groups
from scheduler import start_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables and start scheduler
    Base.metadata.create_all(bind=engine)
    # Temporarily disable scheduler due to enum issues
    # start_scheduler()
    yield
    # Shutdown: cleanup if needed

app = FastAPI(
    title="Masjid Online Class Portal API",
    description="Backend API for Masjid online class management system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
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

@app.get("/")
def read_root():
    return {"message": "Masjid Online Class Portal API", "status": "running"}

@app.get("/api/health")
def health_check():
    return {"status": "OK", "message": "API is healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
