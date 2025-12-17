"""
Script to fix template database - clears all entries and re-registers from actual files
This ensures database IDs match the actual file UUIDs
"""
import sqlite3
import os
import json
from datetime import datetime
import re
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.cai_contact_extractor import extract_cai_contact_from_template

def fix_template_database():
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
    
    # Clear existing templates
    print("🧹 Clearing existing template entries...")
    cursor.execute('DELETE FROM templates')
    conn.commit()
    print("✅ Database cleared")
    
    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            filename TEXT NOT NULL,
            file_type TEXT NOT NULL,
            upload_date TEXT NOT NULL,
            format_data TEXT NOT NULL,
            cai_contact TEXT
        )
    ''')
    
    print(f"📂 Scanning folder: {templates_folder}")
    
    # Scan for template files
    template_files = [f for f in os.listdir(templates_folder) if f.endswith('.docx')]
    print(f"📄 Found {len(template_files)} .docx files")
    
    added = 0
    
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
                continue
            
            # Clean up the display name
            name = original_name.replace('_resume_template', '').replace('_Resume_Template', '')
            name = name.replace('_', ' ').replace('-', ' ')
            name = re.sub(r'\s+\d+$', '', name)  # Remove trailing numbers
            name = re.sub(r'\s+\(\d+\)$', '', name)  # Remove (2), (3), etc.
            name = name.strip().title()
            
            # Format data (minimal)
            format_data = json.dumps({
                "analyzed": False,
                "sections": [],
                "placeholders": []
            })
            
            # Extract CAI contact from template
            template_path = os.path.join(templates_folder, filename)
            cai_contact = None
            cai_contact_json = None
            try:
                cai_contact = extract_cai_contact_from_template(template_path)
                cai_contact_json = json.dumps(cai_contact) if cai_contact else None
            except Exception as e:
                print(f"   ⚠️  Could not extract CAI contact: {str(e)[:100]}")
                pass
            
            # Insert into database
            cursor.execute('''
                INSERT INTO templates (id, name, filename, file_type, upload_date, format_data, cai_contact)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (template_id, name, filename, 'docx', datetime.now().isoformat(), format_data, cai_contact_json))
            
            if cai_contact:
                print(f"✅ Added: {name} (ID: {template_id}) - CAI: {cai_contact.get('name', 'N/A')} ({cai_contact.get('state', 'N/A')})")
            else:
                print(f"✅ Added: {name} (ID: {template_id}) - No CAI contact")
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
    print(f"✅ Done! Template database is now synchronized with actual files.")
    print(f"\n💡 The changes are effective immediately - no restart needed.")

if __name__ == '__main__':
    print("🔧 Fixing template database to match actual files...")
    fix_template_database()
