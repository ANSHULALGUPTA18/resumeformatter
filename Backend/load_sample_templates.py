import sqlite3
import os
import shutil
import uuid
from datetime import datetime

# Sample template files
sample_folder = '../templates sample.db'
templates_folder = 'Static/uploads/templates'

# Ensure templates folder exists
os.makedirs(templates_folder, exist_ok=True)

# Template files to load
template_files = [
    'ar_resume_template.doc',
    'connecticut_resume_template.docx',
    'florida_resume_template.doc',
    'georgia_resume_template.doc',
    'ia_resume_template (2).doc',
    'idaho_resume_template.doc',
    'indiana_resume_template.doc',
    'North-Dakota_Resume_Template_2024.docx',
    'TG Letterhead Resume Template.docx',
    'Virginia-Template-Revised.doc'
]

def load_templates():
    conn = sqlite3.connect('templates.db')
    cursor = conn.cursor()
    
    # Clear existing templates
    cursor.execute('DELETE FROM templates')
    print('🗑️ Cleared existing templates')
    
    added = 0
    for filename in template_files:
        source_path = os.path.join(sample_folder, filename)
        
        if not os.path.exists(source_path):
            print(f'⚠️ Skipping {filename} - file not found')
            continue
        
        # Generate unique ID
        template_id = str(uuid.uuid4())
        
        # Clean up name
        name = filename.replace('_resume_template', '').replace('_Resume_Template', '')
        name = name.replace('.doc', '').replace('.docx', '').replace('_', ' ').replace(' (2)', '')
        name = name.title()
        
        # Get file extension
        file_ext = 'docx' if filename.endswith('.docx') else 'doc'
        
        # Copy file to templates folder with UUID
        dest_filename = f'{template_id}_{filename}'
        dest_path = os.path.join(templates_folder, dest_filename)
        shutil.copy2(source_path, dest_path)
        
        # Insert into database with minimal format_data
        format_data = '{"analyzed": false}'
        cursor.execute('''
            INSERT INTO templates (id, name, filename, file_type, upload_date, format_data)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (template_id, name, dest_filename, file_ext, datetime.now().isoformat(), format_data))
        
        print(f'✅ Added: {name} ({template_id})')
        added += 1
    
    conn.commit()
    
    # Display all templates
    cursor.execute('SELECT id, name, filename FROM templates')
    all_templates = cursor.fetchall()
    
    print(f'\n📋 Total templates loaded: {len(all_templates)}')
    for row in all_templates:
        print(f'  • {row[1]}')
        print(f'    ID: {row[0]}')
        print(f'    File: {row[2]}')
    
    conn.close()
    print(f'\n✅ Successfully loaded {added} sample templates!')

if __name__ == '__main__':
    load_templates()
