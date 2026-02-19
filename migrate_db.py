"""
Database migration script to add new columns to existing tables
"""
from sqlalchemy import text, create_engine

# Explicitly use PostgreSQL
DATABASE_URL = "postgresql://postgres:umar123@localhost:5432/masjid_portal"
engine = create_engine(DATABASE_URL)

def migrate_users_table():
    """Add country, city, timezone columns to users table"""
    with engine.connect() as connection:
        # Check if columns exist before adding them
        try:
            # Try to add country column
            connection.execute(text("ALTER TABLE users ADD COLUMN country VARCHAR"))
            print("✓ Added 'country' column to users table")
        except Exception as e:
            if "already exists" in str(e):
                print("✓ 'country' column already exists")
            else:
                print(f"! Error adding 'country' column: {e}")
        
        try:
            # Try to add city column
            connection.execute(text("ALTER TABLE users ADD COLUMN city VARCHAR"))
            print("✓ Added 'city' column to users table")
        except Exception as e:
            if "already exists" in str(e):
                print("✓ 'city' column already exists")
            else:
                print(f"! Error adding 'city' column: {e}")
        
        try:
            # Try to add timezone column
            connection.execute(text("ALTER TABLE users ADD COLUMN timezone VARCHAR DEFAULT 'UTC'"))
            print("✓ Added 'timezone' column to users table")
        except Exception as e:
            if "already exists" in str(e):
                print("✓ 'timezone' column already exists")
            else:
                print(f"! Error adding 'timezone' column: {e}")
        
        connection.commit()

def migrate_courses_table():
    """Add currency column to courses table"""
    with engine.connect() as connection:
        try:
            # Try to add currency column
            connection.execute(text("ALTER TABLE courses ADD COLUMN currency VARCHAR DEFAULT 'USD'"))
            print("✓ Added 'currency' column to courses table")
        except Exception as e:
            if "already exists" in str(e):
                print("✓ 'currency' column already exists")
            else:
                print(f"! Error adding 'currency' column: {e}")
        
        connection.commit()

if __name__ == "__main__":
    print("Starting database migration...")
    print("\nMigrating users table:")
    migrate_users_table()
    print("\nMigrating courses table:")
    migrate_courses_table()
    print("\n✓ Migration complete!")
