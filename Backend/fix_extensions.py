import sqlite3
import os
import shutil

templates_folder = 'Static/uploads/templates'

def fix_doc_extensions():
    conn = sqlite3.connect('templates.db')
    cursor = conn.cursor()
    
    # Get all .doc templates
    cursor.execute('SELECT id, name, filename, file_type FROM templates WHERE file_type = "doc"')
    doc_templates = cursor.fetchall()
    
    print(f'🔧 Fixing {len(doc_templates)} .doc files...\n')
    
    for template_id, name, old_filename, file_type in doc_templates:
        old_path = os.path.join(templates_folder, old_filename)
        
        if not os.path.exists(old_path):
            print(f'⚠️  {name}: File not found')
            continue
        
        # Change extension to .docx
        new_filename = old_filename.replace('.doc', '.docx')
        new_path = os.path.join(templates_folder, new_filename)
        
        # Rename file
        shutil.move(old_path, new_path)
        
        # Update database
        cursor.execute('''
            UPDATE templates 
            SET filename = ?, file_type = ?
            WHERE id = ?
        ''', (new_filename, 'docx', template_id))
        
        print(f'✅ {name}: {old_filename} → {new_filename}')
    
    conn.commit()
    conn.close()
    print(f'\n✅ Fixed all .doc extensions to .docx!')

if __name__ == '__main__':
    fix_doc_extensions()
