from database import engine, Base
from models import *

# Drop all tables
print("Dropping all tables...")
Base.metadata.drop_all(bind=engine)

# Recreate all tables with fresh schema
print("Creating all tables...")
Base.metadata.create_all(bind=engine)

print("\n✅ Database schema recreated successfully!")
print("All tables and enum types have been recreated with correct lowercase values.")
print("\nIMPORTANT: You'll need to run seed_data.py again to populate the database.")
