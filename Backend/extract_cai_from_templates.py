"""
Script to extract CAI contacts from all existing templates and update database
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from models.persistent_database import get_persistent_template_db
from utils.cai_contact_extractor import extract_cai_contact_from_template

def extract_and_update_cai_contacts():
    """Extract CAI contacts from all templates and update database"""
    
    db = get_persistent_template_db()
    
    # Get all templates
    templates = db.get_all_templates()
    
    print(f"📊 Found {len(templates)} templates in database\n")
    
    updated_count = 0
    no_contact_count = 0
    
    for template in templates:
        template_id = template.get('id')
        template_name = template.get('name', 'Unknown')
        
        # Get template file path
        template_dir = os.path.join('static', 'uploads', 'templates')
        template_path = os.path.join(template_dir, f"{template_id}.docx")
        
        if not os.path.exists(template_path):
            print(f"❌ Template file not found: {template_name} ({template_id})")
            continue
        
        print(f"🔍 Processing: {template_name}")
        
        # Extract CAI contact
        cai_contact = extract_cai_contact_from_template(template_path)
        
        if cai_contact:
            # Update database
            db.update_template_cai_contact(template_id, cai_contact)
            print(f"   ✅ CAI Contact extracted:")
            print(f"      Name: {cai_contact.get('name', 'N/A')}")
            print(f"      Phone: {cai_contact.get('phone', 'N/A')}")
            print(f"      Email: {cai_contact.get('email', 'N/A')}")
            print(f"      State: {cai_contact.get('state', 'N/A')}\n")
            updated_count += 1
        else:
            print(f"   ⚠️  No CAI contact found in template\n")
            no_contact_count += 1
    
    print(f"\n" + "="*60)
    print(f"📈 Summary:")
    print(f"   Total templates: {len(templates)}")
    print(f"   Updated with CAI contact: {updated_count}")
    print(f"   No CAI contact found: {no_contact_count}")
    print("="*60)

if __name__ == "__main__":
    extract_and_update_cai_contacts()
