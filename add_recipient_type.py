"""
Migration: Add recipient_type column to admin_messages table
"""
from sqlalchemy import text
from database import engine, SessionLocal

def migrate():
    print("=" * 80)
    print("MIGRATION: Adding recipient_type to admin_messages table")
    print("=" * 80)
    
    db = SessionLocal()
    
    try:
        # Check if column already exists
        inspect_query = """
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'admin_messages' AND column_name = 'recipient_type'
        """
        result = db.execute(text(inspect_query)).fetchone()
        
        if result:
            print("\n✓ Column 'recipient_type' already exists in admin_messages table")
            return
        
        # Add the column
        print("\n→ Adding 'recipient_type' column...")
        alter_query = """
        ALTER TABLE admin_messages 
        ADD COLUMN recipient_type VARCHAR DEFAULT 'admin' NOT NULL
        """
        db.execute(text(alter_query))
        db.commit()
        print("✓ Column added successfully!")
        
        # Verify
        verify_query = """
        SELECT column_name, data_type FROM information_schema.columns 
        WHERE table_name = 'admin_messages' AND column_name = 'recipient_type'
        """
        result = db.execute(text(verify_query)).fetchone()
        if result:
            print(f"✓ Verified: {result[0]} ({result[1]})")
        
        print("\n" + "=" * 80)
        print("Migration completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ Error during migration: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
