import psycopg2

conn = psycopg2.connect('postgresql://postgres:bZ2BD!RLXb_s9-c@efdvqqbkykonjawgrpos.supabase.co:5432/postgres')
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
