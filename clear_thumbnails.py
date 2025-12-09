"""
Clear existing thumbnails to force regeneration with new system
"""

import requests

APP_URL = "https://resume-formatter.reddesert-f6724e64.centralus.azurecontainerapps.io"

def get_templates():
    """Get all templates"""
    try:
        response = requests.get(f"{APP_URL}/api/templates")
        if response.status_code == 200:
            data = response.json()
            return data.get('templates', [])
        return []
    except Exception as e:
        print(f"Error getting templates: {e}")
        return []

def clear_template_thumbnail(template_id):
    """Clear thumbnail for a specific template by requesting it (forces regeneration)"""
    try:
        # Request the thumbnail - this will trigger regeneration
        response = requests.get(f"{APP_URL}/api/templates/{template_id}/thumbnail")
        if response.status_code == 200:
            print(f"✅ Thumbnail regenerated for: {template_id}")
            return True
        else:
            print(f"❌ Failed to regenerate thumbnail for: {template_id} (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Error regenerating thumbnail for {template_id}: {e}")
        return False

def main():
    print("🔄 THUMBNAIL REGENERATION SCRIPT")
    print("=" * 50)
    
    templates = get_templates()
    if not templates:
        print("❌ No templates found")
        return
    
    print(f"📊 Found {len(templates)} templates")
    print("🔄 Regenerating thumbnails with new system...")
    
    success_count = 0
    for i, template in enumerate(templates, 1):
        template_id = template.get('id')
        template_name = template.get('name', 'Unknown')
        
        print(f"\n[{i}/{len(templates)}] {template_name} ({template_id[:8]}...)")
        
        if clear_template_thumbnail(template_id):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"✅ Successfully regenerated: {success_count}/{len(templates)} thumbnails")
    print("🎉 New document-style thumbnails should now be visible!")
    print("=" * 50)

if __name__ == "__main__":
    main()
