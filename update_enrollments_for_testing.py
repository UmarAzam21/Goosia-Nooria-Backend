"""
Check and update enrollment statuses for testing
"""

from database import SessionLocal
from models import Enrollment, PaymentStatus, EnrollmentStatus, Payment
from datetime import datetime

db = SessionLocal()

print("\nCurrent Enrollments:")
print("─" * 70)

enrollments = db.query(Enrollment).all()

for e in enrollments:
    can_join = e.enrollment_status == EnrollmentStatus.APPROVED and e.payment_status == PaymentStatus.COMPLETED
    print(f"ID: {e.id} | Status: {e.enrollment_status} | Payment: {e.payment_status} | Can Join: {can_join}")
    print(f"    Jitsi Link: {e.jitsi_link[:50]}..." if e.jitsi_link else "    No Jitsi Link")

# Update all enrollments to approved with completed payment for testing
print("\n" + "─" * 70)
print("Updating enrollments for testing...")

for e in enrollments:
    e.enrollment_status = EnrollmentStatus.APPROVED
    e.payment_status = PaymentStatus.COMPLETED
    
    # Create payment record if not exists
    existing_payment = db.query(Payment).filter(Payment.enrollment_id == e.id).first()
    if not existing_payment:
        payment = Payment(
            enrollment_id=e.id,
            amount=1000.0,
            payment_method=e.payment_method,
            payment_status=PaymentStatus.COMPLETED,
            transaction_id=f"TEST-{e.id}-{datetime.now().timestamp()}",
            payment_date=datetime.now()
        )
        db.add(payment)

db.commit()

print("\nUpdated Enrollments:")
print("─" * 70)

# Refresh and display
enrollments = db.query(Enrollment).all()
for e in enrollments:
    can_join = e.enrollment_status == EnrollmentStatus.APPROVED and e.payment_status == PaymentStatus.COMPLETED
    print(f"ID: {e.id} | Status: {e.enrollment_status} | Payment: {e.payment_status} | Can Join: {can_join}")
    print(f"    Jitsi Link: {e.jitsi_link}")

db.close()

print("\n✅ Enrollments updated! Students can now join classes.")
print("\nTest URLs for browser:")
for e in enrollments[:2]:
    print(f"  {e.jitsi_link}")
