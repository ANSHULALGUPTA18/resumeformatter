import sqlite3

conn = sqlite3.connect('templates.db')
cursor = conn.cursor()

try:
    cursor.execute('ALTER TABLE templates ADD COLUMN cai_contact TEXT')
    conn.commit()
    print('✅ Column added successfully')
except Exception as e:
    print(f'ℹ️ {e}')

conn.close()
