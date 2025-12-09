import sqlite3

conn = sqlite3.connect('Backend/templates.db')
cursor = conn.cursor()

# Keep only templates with successful thumbnails
keep_ids = [
    '25e0a3e3-42e7-4f45-8243-68fc616c7b95',  # Connecticutx
    'c02f306a-735b-4c0e-ae80-3976c4b7f513',  # North-Dakota 2024X
    '908dc691-d47e-49a3-acf1-dd35ba3e4da9'   # Tg Letterhead Resume Templatex
]

# Delete templates without thumbnails
placeholders = ','.join('?' * len(keep_ids))
cursor.execute(f'DELETE FROM templates WHERE id NOT IN ({placeholders})', keep_ids)

deleted = cursor.rowcount
conn.commit()

# Show remaining templates
cursor.execute('SELECT id, name FROM templates')
templates = cursor.fetchall()

print(f'🗑️ Removed {deleted} templates without thumbnails')
print(f'\n📋 Remaining templates with thumbnails:')
for row in templates:
    print(f'  ✅ {row[1]} ({row[0]})')

conn.close()
