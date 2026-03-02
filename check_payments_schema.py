import psycopg2

conn = psycopg2.connect('postgresql://postgres:umar123@localhost:5432/masjid_portal')
cur = conn.cursor()

# Get payments table columns
cur.execute("""
    SELECT column_name, data_type, is_nullable 
    FROM information_schema.columns 
    WHERE table_name='payments' 
    ORDER BY ordinal_position
""")

print('PAYMENTS TABLE COLUMNS:')
print('=' * 70)
for row in cur.fetchall():
    print(f'{row[0]:30} | {row[1]:20} | Nullable: {row[2]}')

cur.close()
conn.close()
