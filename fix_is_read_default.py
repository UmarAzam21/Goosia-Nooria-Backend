from database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

try:
    # Set the default value for is_read column
    db.execute(text("ALTER TABLE admin_messages ALTER COLUMN is_read SET DEFAULT false"))
    db.commit()
    print("✓ Updated is_read column default to false")
    
    # Also set is_responded default
    db.execute(text("ALTER TABLE admin_messages ALTER COLUMN is_responded SET DEFAULT false"))
    db.commit()
    print("✓ Updated is_responded column default to false")
    
    # Set existing NULL values to false
    db.execute(text("UPDATE admin_messages SET is_read = false WHERE is_read IS NULL"))
    db.commit()
    print("✓ Updated all NULL is_read values to false")
    
    db.execute(text("UPDATE admin_messages SET is_responded = false WHERE is_responded IS NULL"))
    db.commit()
    print("✓ Updated all NULL is_responded values to false")
    
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()

