import psycopg2

# Database connection parameters
DB_NAME = "masjid_portal"
DB_USER = "postgres"
DB_PASSWORD = "umar123"
DB_HOST = "localhost"
DB_PORT = "5432"

try:
    # Connect to the database
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    print("Fixing all enum values to match Python enum definitions...\n")
    
    # Fix PaymentStatus enum
    print("1. Fixing PaymentStatus enum...")
    # Convert column to varchar
    cur.execute("ALTER TABLE enrollments ALTER COLUMN payment_status TYPE varchar(50);")
    cur.execute("ALTER TABLE payments ALTER COLUMN payment_status TYPE varchar(50);")
    # Update data to lowercase
    cur.execute("UPDATE enrollments SET payment_status = LOWER(payment_status);")
    cur.execute("UPDATE payments SET payment_status = LOWER(payment_status);")
    # Drop and recreate enum
    cur.execute("DROP TYPE IF EXISTS paymentstatus CASCADE;")
    cur.execute("CREATE TYPE paymentstatus AS ENUM ('pending', 'completed', 'failed');")
    # Convert column back to enum
    cur.execute("""
        ALTER TABLE enrollments 
        ALTER COLUMN payment_status TYPE paymentstatus 
        USING payment_status::paymentstatus;
    """)
    cur.execute("""
        ALTER TABLE payments 
        ALTER COLUMN payment_status TYPE paymentstatus 
        USING payment_status::paymentstatus;
    """)
    print("✓ PaymentStatus enum fixed\n")
    
    # Fix EnrollmentStatus enum (already done but ensure it's correct)
    print("2. Fixing EnrollmentStatus enum...")
    cur.execute("ALTER TABLE enrollments ALTER COLUMN enrollment_status TYPE varchar(50);")
    cur.execute("DROP TYPE IF EXISTS enrollmentstatus CASCADE;")
    cur.execute("CREATE TYPE enrollmentstatus AS ENUM ('pending_teacher', 'approved', 'rejected');")
    cur.execute("""
        ALTER TABLE enrollments 
        ALTER COLUMN enrollment_status TYPE enrollmentstatus 
        USING enrollment_status::enrollmentstatus;
    """)
    print("✓ EnrollmentStatus enum fixed\n")
    
    # Fix ClassStatus enum
    print("3. Fixing ClassStatus enum...")
    cur.execute("ALTER TABLE classes ALTER COLUMN status TYPE varchar(50);")
    cur.execute("UPDATE classes SET status = LOWER(status);")
    cur.execute("DROP TYPE IF EXISTS classstatus CASCADE;")
    cur.execute("CREATE TYPE classstatus AS ENUM ('scheduled', 'in_progress', 'completed', 'cancelled');")
    cur.execute("""
        ALTER TABLE classes 
        ALTER COLUMN status TYPE classstatus 
        USING status::classstatus;
    """)
    print("✓ ClassStatus enum fixed\n")
    
    # Fix AttendanceStatus enum
    print("4. Fixing AttendanceStatus enum...")
    cur.execute("ALTER TABLE classes ALTER COLUMN attendance_status TYPE varchar(50);")
    cur.execute("UPDATE classes SET attendance_status = LOWER(attendance_status);")
    cur.execute("DROP TYPE IF EXISTS attendancestatus CASCADE;")
    cur.execute("CREATE TYPE attendancestatus AS ENUM ('pending', 'present', 'absent');")
    cur.execute("""
        ALTER TABLE classes 
        ALTER COLUMN attendance_status TYPE attendancestatus 
        USING attendance_status::attendancestatus;
    """)
    print("✓ AttendanceStatus enum fixed\n")
    
    # Fix PaymentMethod enum
    print("5. Fixing PaymentMethod enum...")
    cur.execute("ALTER TABLE enrollments ALTER COLUMN payment_method TYPE varchar(50);")
    cur.execute("ALTER TABLE payments ALTER COLUMN payment_method TYPE varchar(50);")
    cur.execute("UPDATE enrollments SET payment_method = LOWER(payment_method);")
    cur.execute("UPDATE payments SET payment_method = LOWER(payment_method);")
    cur.execute("DROP TYPE IF EXISTS paymentmethod CASCADE;")
    cur.execute("CREATE TYPE paymentmethod AS ENUM ('jazzcash', 'easypaisa', 'bank_transfer', 'at_masjid');")
    cur.execute("""
        ALTER TABLE enrollments 
        ALTER COLUMN payment_method TYPE paymentmethod 
        USING payment_method::paymentmethod;
    """)
    cur.execute("""
        ALTER TABLE payments 
        ALTER COLUMN payment_method TYPE paymentmethod 
        USING payment_method::paymentmethod;
    """)
    print("✓ PaymentMethod enum fixed\n")
    
    # Fix UserRole enum
    print("6. Fixing UserRole enum...")
    cur.execute("ALTER TABLE users ALTER COLUMN role TYPE varchar(50);")
    cur.execute("UPDATE users SET role = LOWER(role);")
    cur.execute("DROP TYPE IF EXISTS userrole CASCADE;")
    cur.execute("CREATE TYPE userrole AS ENUM ('student', 'teacher', 'admin');")
    cur.execute("""
        ALTER TABLE users 
        ALTER COLUMN role TYPE userrole 
        USING role::userrole;
    """)
    print("✓ UserRole enum fixed\n")
    
    print("\n✅ All enum values fixed successfully!")
    print("All enums now use lowercase values matching Python enum definitions.")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
