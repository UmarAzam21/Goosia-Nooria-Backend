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
    
    print("Fixing enrollment_status enum values...")
    
    # Drop the existing enum type if it has wrong values
    # First, we need to ALTER the column to use a temporary type
    cur.execute("""
        ALTER TABLE enrollments 
        ALTER COLUMN enrollment_status TYPE varchar(50);
    """)
    print("✓ Converted column to varchar")
    
    # Drop the old enum type
    cur.execute("""
        DROP TYPE IF EXISTS enrollmentstatus CASCADE;
    """)
    print("✓ Dropped old enum type")
    
    # Create the enum type with correct values (lowercase)
    cur.execute("""
        CREATE TYPE enrollmentstatus AS ENUM ('pending_teacher', 'approved', 'rejected');
    """)
    print("✓ Created new enum type with correct values")
    
    # Convert the column back to enum type
    cur.execute("""
        ALTER TABLE enrollments 
        ALTER COLUMN enrollment_status TYPE enrollmentstatus 
        USING enrollment_status::enrollmentstatus;
    """)
    print("✓ Converted column back to enum type")
    
    print("\n✅ Enum values fixed successfully!")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
