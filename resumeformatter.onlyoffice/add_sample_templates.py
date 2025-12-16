import sqlite3
import uuid
from datetime import datetime

# Sample template data
sample_templates = [
    {'name': 'Florida', 'file_type': 'docx'},
    {'name': 'Indiana', 'file_type': 'docx'},
    {'name': 'Idaho', 'file_type': 'docx'},
    {'name': 'Arkansas', 'file_type': 'docx'},
    {'name': 'Georgia', 'file_type': 'docx'},
    {'name': 'Connecticut', 'file_type': 'docx'},
    {'name': 'Virginia', 'file_type': 'docx'},
    {'name': 'North Dakota', 'file_type': 'docx'},
]

def add_sample_templates():
    conn = sqlite3.connect('Backend/templates.db')
    cursor = conn.cursor()
    
    # Clear existing templates
    cursor.execute('DELETE FROM templates')
    print('🗑️ Cleared existing templates\n')
    
    added = 0
    for template in sample_templates:
        template_id = str(uuid.uuid4())
        name = template['name']
        filename = f"{template_id}_{name.lower().replace(' ', '_')}_resume_template.{template['file_type']}"
        file_type = template['file_type']
        format_data = '{"placeholder": true}'
        
        cursor.execute('''
            INSERT INTO templates (id, name, filename, file_type, upload_date, format_data)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (template_id, name, filename, file_type, datetime.now().isoformat(), format_data))
        
        print(f'✅ Added: {name}')
        print(f'   ID: {template_id}')
        print(f'   File: {filename}\n')
        added += 1
    
    conn.commit()
    
    # Display all templates
    cursor.execute('SELECT id, name FROM templates')
    all_templates = cursor.fetchall()
    
    print(f'📋 Total templates in database: {len(all_templates)}')
    for row in all_templates:
        print(f'  • {row[1]} ({row[0]})')
    
    conn.close()
    print(f'\n✅ Successfully added {added} sample templates!')

if __name__ == '__main__':
    add_sample_templates()
