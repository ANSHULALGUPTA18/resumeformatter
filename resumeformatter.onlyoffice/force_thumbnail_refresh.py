"""
Force thumbnail refresh by clearing Azure Storage cache
"""

import requests
import json

APP_URL = "https://resume-formatter.reddesert-f6724e64.centralus.azurecontainerapps.io"

def delete_template_thumbnail(template_id):
    """Delete a template's thumbnail to force regeneration"""
    try:
        response = requests.delete(f"{APP_URL}/api/templates/{template_id}/thumbnail")
        if response.status_code in [200, 204, 404]:  # 404 is OK if thumbnail doesn't exist
            print(f"✅ Thumbnail cache cleared for: {template_id}")
            return True
        else:
            print(f"⚠️ Failed to clear thumbnail for: {template_id} (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Error clearing thumbnail for {template_id}: {e}")
        return False

def regenerate_thumbnail(template_id):
    """Force regenerate thumbnail by requesting it with cache-busting"""
    try:
        # Add timestamp to bust cache
        import time
        timestamp = int(time.time())
        response = requests.get(f"{APP_URL}/api/templates/{template_id}/thumbnail?t={timestamp}")
        if response.status_code == 200:
            print(f"✅ New thumbnail generated for: {template_id}")
            return True
        else:
            print(f"❌ Failed to generate thumbnail for: {template_id} (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Error generating thumbnail for {template_id}: {e}")
        return False

def main():
    print("🔄 FORCE THUMBNAIL REFRESH")
    print("=" * 50)
    
    # Get templates
    try:
        response = requests.get(f"{APP_URL}/api/templates")
        if response.status_code == 200:
            data = response.json()
            templates = data.get('templates', [])
        else:
            print(f"❌ Failed to get templates: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error getting templates: {e}")
        return
    
    if not templates:
        print("❌ No templates found")
        return
    
    print(f"📊 Found {len(templates)} templates")
    print("🗑️ Clearing thumbnail cache...")
    
    # Step 1: Clear existing thumbnails
    for template in templates:
        template_id = template.get('id')
        template_name = template.get('name', 'Unknown')
        print(f"\n🗑️ Clearing cache for: {template_name}")
        delete_template_thumbnail(template_id)
    
    print("\n🔄 Regenerating thumbnails...")
    
    # Step 2: Force regenerate with new system
    success_count = 0
    for i, template in enumerate(templates, 1):
        template_id = template.get('id')
        template_name = template.get('name', 'Unknown')
        
        print(f"\n[{i}/{len(templates)}] Regenerating: {template_name}")
        if regenerate_thumbnail(template_id):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"✅ Successfully refreshed: {success_count}/{len(templates)} thumbnails")
    print("🔄 Clear your browser cache and refresh the page!")
    print("=" * 50)

if __name__ == "__main__":
    main()
