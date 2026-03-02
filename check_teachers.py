#!/usr/bin/env python3
from database import SessionLocal
from models import User, Teacher

db = SessionLocal()

print('Users with teacher role:')
teachers_users = db.query(User).filter(User.role == 'teacher').all()
for u in teachers_users:
    print(f'  {u.id}: {u.email}')

print('\nTeacher records:')
teachers = db.query(Teacher).all()
print(f'Total teacher records: {len(teachers)}')
for t in teachers:
    user_email = t.user.email if t.user else "N/A"
    print(f'  ID: {t.id}, User: {user_email}')

db.close()
