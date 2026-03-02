"""Add sender_id column to admin_messages table"""

from sqlalchemy import text
from database import SessionLocal, engine

def migrate():
    with engine.connect() as connection:
        # Add sender_id column if it doesn't exist
        try:
            connection.execute(text("""
                ALTER TABLE admin_messages 
                ADD COLUMN sender_id INTEGER
            """))
            connection.commit()
            print("✅ Added sender_id column to admin_messages")
        except Exception as e:
            if "already exists" in str(e):
                print("ℹ️  sender_id column already exists")
            else:
                print(f"❌ Error adding column: {e}")
        
        # Set sender_id = student_id for existing messages (they were sent by students)
        try:
            connection.execute(text("""
                UPDATE admin_messages 
                SET sender_id = student_id 
                WHERE sender_id IS NULL
            """))
            connection.commit()
            print("✅ Set sender_id for existing messages")
        except Exception as e:
            print(f"ℹ️  Could not update sender_id: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("MIGRATION: Add sender_id to admin_messages")
    print("=" * 60)
    migrate()
    print("✅ Migration complete!")
