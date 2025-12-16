import sqlite3
import os
from utils.document_thumbnail import create_docx_preview_thumbnail

templates_folder = 'Static/uploads/templates'
thumbnails_folder = 'Static/thumbnails'

# Ensure thumbnails folder exists
os.makedirs(thumbnails_folder, exist_ok=True)

def generate_all_thumbnails():
    conn = sqlite3.connect('templates.db')
    cursor = conn.cursor()
    
    # Get all templates
    cursor.execute('SELECT id, name, filename FROM templates')
    templates = cursor.fetchall()
    
    print(f'🖼️  Generating thumbnails for {len(templates)} templates...\n')
    
    success = 0
    failed = 0
    
    for template_id, name, filename in templates:
        template_path = os.path.join(templates_folder, filename)
        thumbnail_path = os.path.join(thumbnails_folder, f'{template_id}.png')
        
        if not os.path.exists(template_path):
            print(f'❌ {name}: Template file not found')
            failed += 1
            continue
        
        try:
            # Generate thumbnail
            result = create_docx_preview_thumbnail(template_path, thumbnail_path)
            
            if result:
                print(f'✅ {name}: Thumbnail generated')
                success += 1
            else:
                print(f'⚠️  {name}: Thumbnail generation returned None')
                failed += 1
        except Exception as e:
            print(f'❌ {name}: Error - {str(e)}')
            failed += 1
    
    conn.close()
    
    print(f'\n📊 Summary:')
    print(f'   ✅ Success: {success}')
    print(f'   ❌ Failed: {failed}')
    print(f'   📁 Thumbnails saved to: {thumbnails_folder}')

if __name__ == '__main__':
    generate_all_thumbnails()
