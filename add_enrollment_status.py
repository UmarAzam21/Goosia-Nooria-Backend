import psycopg2
from psycopg2 import sql

# Database connection parameters
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "masjid_portal"
DB_USER = "postgres"
DB_PASSWORD = "umar123"

def add_enrollment_status_column():
    """Add enrollment_status column to enrollments table"""
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        print("Connected to database successfully")
        
        # Check if column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='enrollments' AND column_name='enrollment_status';
        """)
        
        if cursor.fetchone():
            print("Column 'enrollment_status' already exists")
        else:
            # Drop the enum type if it exists (to recreate with correct values)
            cursor.execute("DROP TYPE IF EXISTS enrollmentstatus CASCADE;")
            
            # Create enum type with correct values
            cursor.execute("""
                CREATE TYPE enrollmentstatus AS ENUM ('pending_teacher', 'approved', 'rejected');
            """)
            
            # Add the enrollment_status column with default value
            cursor.execute("""
                ALTER TABLE enrollments 
                ADD COLUMN enrollment_status enrollmentstatus DEFAULT 'pending_teacher'::enrollmentstatus;
            """)
            
            conn.commit()
            print("Successfully added 'enrollment_status' column to enrollments table")
        
        cursor.close()
        conn.close()
        print("Database connection closed")
        
    except Exception as e:
        print(f"Error: {e}")
        if conn:
            conn.rollback()

if __name__ == "__main__":
    add_enrollment_status_column()
