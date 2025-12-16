import sqlite3
import os
import uuid
from datetime import datetime

# Template files in Static/uploads/templates
template_files = {
    '452fa017-e6af-4a4e-99f4-5c9770ce7398': 'florida_resume_template.docx',
    'c0778995-be7e-4594-a757-21a91bc7bfad': 'indiana_resume_template.docx',
    '1a344ff2-0a0d-4867-9c70-67ad6fd6749c': 'idaho_resume_template.docx',
    'f6a9af4f-b8df-4c87-98c5-a43ea27859c8': 'ar_resume_template4.docx',
}

def init_database():
    conn = sqlite3.connect('templates.db')
    cursor = conn.cursor()
    
    # Create templates table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT,
            created_at TEXT,
            thumbnail_path TEXT
        )
    ''')
    
    # Check existing templates
    cursor.execute('SELECT id FROM templates')
    existing_ids = set(row[0] for row in cursor.fetchall())
    
    print(f"Found {len(existing_ids)} existing templates in DB")
    
    # Add templates that don't exist
    added = 0
    for template_id, filename in template_files.items():
        if template_id not in existing_ids:
            name = filename.replace('_resume_template', '').replace('.docx', '').replace('_', ' ').title()
            file_path = f'Static/uploads/templates/{template_id}_{filename}'
            
            cursor.execute('''
                INSERT INTO templates (id, name, file_path, file_type, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (template_id, name, file_path, 'DOCX', datetime.now().isoformat()))
            added += 1
            print(f"✅ Added template: {name} ({template_id})")
    
    conn.commit()
    
    # Display all templates
    cursor.execute('SELECT id, name, file_path FROM templates')
    all_templates = cursor.fetchall()
    
    print(f"\n📋 Total templates in database: {len(all_templates)}")
    for row in all_templates:
        print(f"  • {row[1]} ({row[0]})")
        print(f"    Path: {row[2]}")
    
    conn.close()
    print(f"\n✅ Database initialized! Added {added} new templates.")

if __name__ == '__main__':
    init_database()
