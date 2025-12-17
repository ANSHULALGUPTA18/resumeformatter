"""
Script to scan existing template files and register them in the database
This will find all .docx files in static/uploads/templates and add them to the database
"""
import sqlite3
import os
import json
from datetime import datetime
import re

def scan_and_register_templates():
    # Path to templates folder
    templates_folder = os.path.join('static', 'uploads', 'templates')
    
    # Database path
    db_path = 'templates.db'
    
    if not os.path.exists(templates_folder):
        print(f"❌ Templates folder not found: {templates_folder}")
        return
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            filename TEXT NOT NULL,
            file_type TEXT NOT NULL,
            upload_date TEXT NOT NULL,
            format_data TEXT NOT NULL
        )
    ''')
    
    # Get existing template IDs
    cursor.execute('SELECT id, filename FROM templates')
    existing_templates = {row[1]: row[0] for row in cursor.fetchall()}
    
    print(f"📊 Found {len(existing_templates)} templates already in database")
    print(f"📂 Scanning folder: {templates_folder}")
    
    # Scan for template files
    template_files = [f for f in os.listdir(templates_folder) if f.endswith('.docx')]
    print(f"📄 Found {len(template_files)} .docx files")
    
    added = 0
    updated = 0
    skipped = 0
    
    for filename in template_files:
        try:
            # Extract template ID from filename (UUID_name.docx format)
            match = re.match(r'([a-f0-9\-]{36})_(.+)\.docx', filename)
            
            if match:
                template_id = match.group(1)
                original_name = match.group(2)
            else:
                # If no UUID in filename, skip
                print(f"⚠️  Skipping {filename} - no UUID found in filename")
                skipped += 1
                continue
            
            # Clean up the display name
            name = original_name.replace('_resume_template', '').replace('_Resume_Template', '')
            name = name.replace('_', ' ').replace('-', ' ')
            name = re.sub(r'\s+\d+$', '', name)  # Remove trailing numbers
            name = re.sub(r'\s+\(\d+\)$', '', name)  # Remove (2), (3), etc.
            name = name.strip().title()
            
            # Check if already exists
            if filename in existing_templates:
                print(f"✓ Already registered: {name}")
                skipped += 1
                continue
            
            # Format data (minimal)
            format_data = json.dumps({
                "analyzed": False,
                "sections": [],
                "placeholders": []
            })
            
            # Insert into database
            cursor.execute('''
                INSERT OR REPLACE INTO templates (id, name, filename, file_type, upload_date, format_data)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (template_id, name, filename, 'docx', datetime.now().isoformat(), format_data))
            
            print(f"✅ Added: {name} (ID: {template_id})")
            added += 1
            
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            continue
    
    conn.commit()
    
    # Display final summary
    cursor.execute('SELECT id, name, filename FROM templates ORDER BY name')
    all_templates = cursor.fetchall()
    
    print(f"\n" + "="*70)
    print(f"📋 SUMMARY")
    print(f"="*70)
    print(f"✅ Added: {added}")
    print(f"⏭️  Skipped (already registered): {skipped}")
    print(f"📊 Total templates in database: {len(all_templates)}")
    print(f"\n" + "="*70)
    print(f"📋 ALL TEMPLATES IN DATABASE:")
    print(f"="*70)
    
    for idx, row in enumerate(all_templates, 1):
        print(f"{idx:2d}. {row[1]}")
        print(f"    ID: {row[0]}")
        print(f"    File: {row[2]}")
        print()
    
    conn.close()
    print(f"✅ Done! Templates are now registered and ready to use.")
    print(f"\n💡 Restart your backend server to see the changes.")

if __name__ == '__main__':
    print("🔍 Scanning for templates in static/uploads/templates folder...")
    scan_and_register_templates()
