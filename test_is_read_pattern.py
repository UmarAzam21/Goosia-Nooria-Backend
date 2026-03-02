from database import SessionLocal
from models import AdminMessage

db = SessionLocal()

messages = db.query(AdminMessage).all()

# Group by sender_id
by_sender = {}
for msg in messages:
    sender = msg.sender_id
    if sender not in by_sender:
        by_sender[sender] = {'total': 0, 'read': 0, 'unread': 0}
    by_sender[sender]['total'] += 1
    if msg.is_read:
        by_sender[sender]['read'] += 1
    else:
        by_sender[sender]['unread'] += 1

print('Messages grouped by sender_id:')
for sender_id, counts in by_sender.items():
    print(f'  Sender ID {sender_id}: Total={counts["total"]}, Read={counts["read"]}, Unread={counts["unread"]}')

print('\nMessages by student_id (who received them):')
by_student = {}
for msg in messages:
    student = msg.student_id
    if student not in by_student:
        by_student[student] = {'total': 0, 'read': 0, 'unread': 0}
    by_student[student]['total'] += 1
    if msg.is_read:
        by_student[student]['read'] += 1
    else:
        by_student[student]['unread'] += 1

for student_id, counts in by_student.items():
    print(f'  Student ID {student_id}: Total={counts["total"]}, Read={counts["read"]}, Unread={counts["unread"]}')

db.close()
