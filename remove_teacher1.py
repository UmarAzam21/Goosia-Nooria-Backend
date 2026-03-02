import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    'host': 'localhost',
    'database': 'masjid_portal',
    'user': 'postgres',
    'password': 'umar123'
}

def remove_teacher1():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Find teacher1 user
        cursor.execute("SELECT id, name, email FROM users WHERE name = %s", ('teacher1',))
        user = cursor.fetchone()
        
        if not user:
            print("✗ teacher1 user not found")
            cursor.close()
            conn.close()
            return
        
        user_id = user['id']
        print(f"\n✓ Found teacher1 user:")
        print(f"  ID: {user_id}")
        print(f"  Name: {user['name']}")
        print(f"  Email: {user['email']}")
        
        # Check for Teacher records
        cursor.execute("SELECT id, course_id FROM teachers WHERE user_id = %s", (user_id,))
        teacher_records = cursor.fetchall()
        
        if teacher_records:
            print(f"\n✓ Found {len(teacher_records)} Teacher record(s):")
            for record in teacher_records:
                print(f"  - Teacher ID: {record['id']}, Course ID: {record['course_id']}")
        
        # Step 1: Delete Payments that reference teacher1's enrollments
        cursor.execute("""
            SELECT p.id FROM payments p
            JOIN enrollments e ON p.enrollment_id = e.id
            JOIN time_slots ts ON e.time_slot_id = ts.id
            WHERE ts.teacher_id IN (SELECT id FROM teachers WHERE user_id = %s)
        """, (user_id,))
        payments = cursor.fetchall()
        
        if payments:
            print(f"\n  Found {len(payments)} Payment record(s) to delete first")
            cursor.execute("""
                DELETE FROM payments 
                WHERE enrollment_id IN (
                    SELECT e.id FROM enrollments e
                    JOIN time_slots ts ON e.time_slot_id = ts.id
                    WHERE ts.teacher_id IN (SELECT id FROM teachers WHERE user_id = %s)
                )
            """, (user_id,))
            deleted_payments = cursor.rowcount
            print(f"  ✓ Deleted {deleted_payments} Payment record(s)")
        
        # Step 2: Delete Enrollments that reference teacher1's time slots
        cursor.execute("""
            SELECT e.id FROM enrollments e
            JOIN time_slots ts ON e.time_slot_id = ts.id
            WHERE ts.teacher_id IN (SELECT id FROM teachers WHERE user_id = %s)
        """, (user_id,))
        enrollments = cursor.fetchall()
        
        if enrollments:
            print(f"  Found {len(enrollments)} Enrollment record(s) to delete")
            cursor.execute("""
                DELETE FROM enrollments 
                WHERE time_slot_id IN (
                    SELECT id FROM time_slots 
                    WHERE teacher_id IN (SELECT id FROM teachers WHERE user_id = %s)
                )
            """, (user_id,))
            deleted_enrollments = cursor.rowcount
            print(f"  ✓ Deleted {deleted_enrollments} Enrollment record(s)")
        
        # Step 3: Delete TimeSlots (they reference teachers)
        cursor.execute("SELECT id FROM time_slots WHERE teacher_id IN (SELECT id FROM teachers WHERE user_id = %s)", (user_id,))
        time_slots = cursor.fetchall()
        
        if time_slots:
            print(f"  Found {len(time_slots)} TimeSlot record(s) to delete")
            cursor.execute("DELETE FROM time_slots WHERE teacher_id IN (SELECT id FROM teachers WHERE user_id = %s)", (user_id,))
            deleted_slots = cursor.rowcount
            print(f"  ✓ Deleted {deleted_slots} TimeSlot record(s)")
        
        # Step 4: Delete Teacher records
        if teacher_records:
            cursor.execute("DELETE FROM teachers WHERE user_id = %s", (user_id,))
            deleted_count = cursor.rowcount
            print(f"✓ Deleted {deleted_count} Teacher record(s)")
        
        # Delete User record
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        deleted_user_count = cursor.rowcount
        print(f"✓ Deleted User record (teacher1)")
        
        conn.commit()
        print(f"\n✅ Successfully removed teacher1 from database")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        if conn:
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("REMOVING teacher1 FROM DATABASE")
    print("=" * 60)
    remove_teacher1()
