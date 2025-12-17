"""
Re-analyze all existing templates to detect skill tables
Run this script after updating the skill detection code
"""

import os
import sys
import io

# Set UTF-8 encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.persistent_database import get_persistent_template_db
from models.database import TemplateDB
from utils.advanced_template_analyzer import analyze_template
from config import Config

def reanalyze_all_templates():
    """Re-analyze all templates to add skill table detection"""
    print("\n" + "="*70)
    print("RE-ANALYZING ALL TEMPLATES FOR SKILL TABLES")
    print("="*70 + "\n")

    # Get databases
    persistent_db = get_persistent_template_db()
    local_db = TemplateDB()

    # Try persistent storage first
    print("[*] Fetching templates from persistent storage...")
    templates = persistent_db._get_templates_from_storage()

    if not templates or len(templates) == 0:
        print("[!] No templates in persistent storage, trying local database...")
        templates = []
        local_templates = local_db.get_all_templates()

        # Convert local templates to full format
        for lt in local_templates:
            full_template = local_db.get_template(lt['id'])
            if full_template:
                templates.append(full_template)

    if not templates or len(templates) == 0:
        print("[X] No templates found in any database!")
        return

    print(f"[+] Found {len(templates)} templates to re-analyze\n")

    updated_count = 0

    for template in templates:
        template_id = template['id']
        template_name = template['name']
        filename = template['filename']

        print(f"\n{'='*70}")
        print(f"[*] Re-analyzing: {template_name}")
        print(f"    ID: {template_id}")
        print(f"    File: {filename}")
        print(f"{'='*70}")

        # Get template file path
        template_path = os.path.join(Config.TEMPLATE_FOLDER, filename)

        # Check if file exists
        if not os.path.exists(template_path):
            print(f"[!] Template file not found at: {template_path}")
            print(f"    Trying to download from persistent storage...")

            # Try to download from persistent storage
            download_success = persistent_db.download_template_file(
                template_id,
                filename,
                template_path
            )

            if not download_success:
                print(f"[X] Failed to download template file")
                continue

        # Re-analyze template
        try:
            print(f"\n[*] Analyzing template for skill tables...")
            new_format_data = analyze_template(template_path)

            # Check if skill tables were detected
            skill_tables = []
            if new_format_data and 'tables' in new_format_data:
                skill_tables = [t for t in new_format_data['tables'] if t.get('is_skill_table')]

            if skill_tables:
                print(f"\n[+] SKILL TABLES DETECTED: {len(skill_tables)}")
                for st in skill_tables:
                    categories = st.get('skill_categories', [])
                    print(f"    [*] Skill categories ({len(categories)}): {', '.join(categories[:10])}")
                    if len(categories) > 10:
                        print(f"        ... and {len(categories) - 10} more")
            else:
                print(f"\n[-] No skill tables detected in this template")

            # Update template in database
            template['format_data'] = new_format_data

            # Update in persistent storage
            print(f"\n[*] Updating template in persistent storage...")
            update_success = persistent_db.add_template(
                template_id,
                template_name,
                filename,
                template['file_type'],
                new_format_data,
                template.get('cai_contact')
            )

            if update_success:
                print(f"[+] Template updated successfully")
                updated_count += 1
            else:
                print(f"[X] Failed to update template")

            # Also update local database
            try:
                local_db.add_template(
                    template_id,
                    template_name,
                    filename,
                    template['file_type'],
                    new_format_data
                )
                print(f"[+] Also updated in local database")
            except Exception as e:
                print(f"[!] Failed to update local database: {e}")

        except Exception as e:
            print(f"[X] Error analyzing template: {e}")
            import traceback
            traceback.print_exc()
            continue

    print(f"\n\n" + "="*70)
    print(f"RE-ANALYSIS COMPLETE")
    print(f"="*70)
    print(f"[+] Successfully updated: {updated_count}/{len(templates)} templates")
    print(f"\nPlease refresh your browser to see the Skill Matrix!")
    print(f"="*70 + "\n")

if __name__ == "__main__":
    reanalyze_all_templates()
