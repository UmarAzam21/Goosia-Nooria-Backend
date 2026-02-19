import psycopg2

conn = psycopg2.connect(
    dbname="masjid_portal",
    user="postgres",
    password="umar123",
    host="localhost"
)

cur = conn.cursor()

print("Checking enum type definitions in database:\n")

# Get all enum types
cur.execute("""
    SELECT t.typname, e.enumlabel
    FROM pg_type t 
    JOIN pg_enum e ON t.oid = e.enumtypid  
    JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
    WHERE n.nspname = 'public'
    ORDER BY t.typname, e.enumsortorder;
""")

current_enum = None
for row in cur.fetchall():
    enum_name, enum_value = row
    if enum_name != current_enum:
        if current_enum is not None:
            print()
        print(f"{enum_name}:")
        current_enum = enum_name
    print(f"  - {enum_value}")

cur.close()
conn.close()
