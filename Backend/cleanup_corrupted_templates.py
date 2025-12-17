"""
Cleanup script to remove corrupted template files
Run this if you have templates that won't open/edit
"""

import os
import sys
from docx import Document
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from models.persistent_database import get_persistent_template_db
from models.database import TemplateDB

def check_and_cleanup_templates():
    """Check all templates and remove corrupted ones"""

    print("="*70)
    print("TEMPLATE CLEANUP UTILITY")
    print("="*70)
    print()

    db = TemplateDB()
    persistent_db = get_persistent_template_db()

    # Get all templates
    templates = persistent_db.get_all_templates()
    if not templates:
        templates = db.get_all_templates()

    if not templates:
        print("No templates found.")
        return

    print(f"Found {len(templates)} templates. Checking validity...")
    print()

    corrupted = []
    valid = []

    for template in templates:
        template_id = template['id']
        template_name = template['name']
        template_filename = template['filename']
        template_path = os.path.join(Config.TEMPLATE_FOLDER, template_filename)

        # Download if not local
        if not os.path.exists(template_path):
            print(f"📥 Downloading {template_name}...")
            persistent_db.download_template_file(template_id, template_filename, template_path)

        # Check if valid DOCX
        try:
            doc = Document(template_path)
            # Try to access paragraphs (will fail if corrupted)
            _ = len(doc.paragraphs)
            valid.append(template)
            print(f"✅ Valid: {template_name}")
        except Exception as e:
            corrupted.append(template)
            print(f"❌ Corrupted: {template_name} - {str(e)[:50]}")

    print()
    print("="*70)
    print(f"RESULTS: {len(valid)} valid, {len(corrupted)} corrupted")
    print("="*70)
    print()

    if not corrupted:
        print("✅ All templates are valid!")
        return

    print("Corrupted templates:")
    for template in corrupted:
        print(f"  - {template['name']} (ID: {template['id']})")

    print()
    response = input("Do you want to DELETE these corrupted templates? (yes/no): ")

    if response.lower() in ['yes', 'y']:
        print()
        print("Deleting corrupted templates...")
        for template in corrupted:
            try:
                template_id = template['id']
                template_filename = template['filename']

                # Delete from databases
                db.delete_template(template_id)
                persistent_db.delete_template(template_id)

                # Delete local file
                template_path = os.path.join(Config.TEMPLATE_FOLDER, template_filename)
                if os.path.exists(template_path):
                    os.remove(template_path)

                print(f"  ✅ Deleted: {template['name']}")
            except Exception as e:
                print(f"  ❌ Failed to delete {template['name']}: {e}")

        print()
        print("✅ Cleanup complete!")
    else:
        print("Cleanup cancelled.")

if __name__ == '__main__':
    try:
        check_and_cleanup_templates()
    except KeyboardInterrupt:
        print("\n\nCleanup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
