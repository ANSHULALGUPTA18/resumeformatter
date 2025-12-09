"""
Verify that thumbnails are working correctly
"""

import requests
import time

APP_URL = "https://resume-formatter.reddesert-f6724e64.centralus.azurecontainerapps.io"

def test_thumbnail(template_id, template_name):
    """Test a single thumbnail"""
    try:
        # Add timestamp to bust cache
        timestamp = int(time.time())
        response = requests.get(f"{APP_URL}/api/templates/{template_id}/thumbnail?t={timestamp}")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            content_length = len(response.content)
            
            print(f"✅ {template_name}")
            print(f"   📊 Size: {content_length:,} bytes")
            print(f"   🎨 Type: {content_type}")
            
            # Check if it's a proper image
            if content_type == 'image/png' and content_length > 1000:
                print(f"   🎉 Enhanced thumbnail detected!")
                return True
            else:
                print(f"   ⚠️ Basic thumbnail")
                return False
        else:
            print(f"❌ {template_name} - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {template_name} - Error: {e}")
        return False

def main():
    print("🔍 THUMBNAIL VERIFICATION")
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
    
    print(f"📊 Testing {len(templates)} templates...")
    print()
    
    enhanced_count = 0
    for template in templates:
        template_id = template.get('id')
        template_name = template.get('name', 'Unknown')
        
        if test_thumbnail(template_id, template_name):
            enhanced_count += 1
        print()
    
    print("=" * 50)
    print(f"📈 RESULTS:")
    print(f"   Enhanced thumbnails: {enhanced_count}/{len(templates)}")
    print(f"   Success rate: {(enhanced_count/len(templates)*100):.1f}%")
    
    if enhanced_count == len(templates):
        print("🎉 ALL THUMBNAILS ARE WORKING PERFECTLY!")
    elif enhanced_count > 0:
        print("✅ Most thumbnails are enhanced!")
    else:
        print("⚠️ Thumbnails need improvement")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
