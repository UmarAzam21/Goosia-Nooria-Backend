# Masjid Online Class Portal - Backend

Backend API for the Masjid Online Class Portal built with FastAPI and PostgreSQL.

## Features

- ✅ Student Registration & Authentication
- ✅ Course Management
- ✅ Teacher Assignment & Time Slots
- ✅ Enrollment System
- ✅ Payment Integration (Stripe + At Masjid)
- ✅ Automatic Daily Class Creation
- ✅ Attendance Tracking
- ✅ Real-time Chat System
- ✅ Video Class Integration (Jitsi Meet)
- ✅ Dashboard for Students, Teachers & Admin

## Video Conferencing

Uses **Jitsi Meet** for reliable, instant video conferencing:
- No API keys or complex setup needed
- Students click join link → instant access to video room
- Deterministic room IDs based on class name
- Works immediately without buffering or delays
- URLs: `https://meet.jitsi.net/Noori{room_id}`

## Tech Stack

- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM
- **JWT** - Authentication
- **Stripe** - Payment processing
- **APScheduler** - Automated class scheduling

## Setup

### Prerequisites

- Python 3.9+
- PostgreSQL 12+ with password "umar123"

### Installation

1. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create PostgreSQL database:
```bash
psql -U postgres
CREATE DATABASE masjid_portal;
\q
```

4. Configure environment:
```bash
copy .env.example .env
# Edit .env with your settings
```

5. Run the server:
```bash
python main.py
```

API will be available at: http://localhost:8000
API Documentation: http://localhost:8000/docs

## Database Schema

### Users
- Students, Teachers, Admins

### Courses
- Name, Description, Duration, Fee

### Teachers
- Linked to User, Assigned to Course
- Time Slots (Day, Start/End Time)

### Enrollments
- Student enrolls in Course with Teacher
- Auto-calculates end date based on course duration
- Links to Payment

### Payments
- Online (Stripe) or At Masjid
- Status: Pending, Completed, Failed

### Classes
- Auto-generated daily based on enrollment time slots
- Zoom links automatically created
- Attendance tracking

### Chat Messages
- Between students and teachers
- Class-specific or direct messages

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login (returns JWT token)

### Courses
- `GET /api/courses` - List all courses
- `GET /api/courses/{id}` - Get course details
- `POST /api/courses` - Create course (Admin)

### Teachers
- `GET /api/teachers?course_id={id}` - List teachers by course
- `GET /api/teachers/{id}/time-slots` - Get teacher time slots

### Enrollments
- `POST /api/enrollments` - Create enrollment
- `GET /api/enrollments/my-enrollments` - Get my enrollments

### Classes
- `GET /api/classes/my-classes?date_filter=today` - Get my classes
- `POST /api/classes/{id}/join` - Join class (marks attendance)
- `PUT /api/classes/{id}/upload` - Upload materials (Teacher)

### Payments
- `POST /api/payments/create-payment-intent` - Create Stripe payment
- `POST /api/payments/confirm-payment/{id}` - Confirm at-masjid payment (Admin)
- `GET /api/payments/my-payments` - Get my payment history

### Chat
- `POST /api/chat` - Send message
- `GET /api/chat/class/{id}` - Get class messages
- `GET /api/chat/unread-count` - Get unread count

### Dashboard
- `GET /api/dashboard/student` - Student dashboard
- `GET /api/dashboard/teacher` - Teacher dashboard
- `GET /api/dashboard/admin` - Admin dashboard

## Automated Features

### Daily Class Creation
- Runs daily at midnight
- Creates class entries for all active enrollments
- Generates Zoom links and meeting IDs automatically
- Only creates classes matching the day of week in time slots

## Authentication

All protected endpoints require JWT token in Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Testing

Use the interactive API docs at http://localhost:8000/docs to test endpoints.

### Sample Flow

1. Register a student
2. Create courses (admin)
3. Create teachers with time slots
4. Student enrolls in a course
5. Process payment
6. System automatically creates daily classes
7. Student/Teacher join classes
8. Chat during class
9. Teacher uploads materials
10. View dashboard

## Deployment

Update the .env file with production values:
- Set strong SECRET_KEY
- Configure production database
- Add Stripe production keys
- Set DEBUG=False

## License

MIT
