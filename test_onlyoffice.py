#!/usr/bin/env python3
"""
Quick test script to verify OnlyOffice integration
"""

import requests
import json

def test_onlyoffice_status():
    """Test if OnlyOffice is running"""
    print("\n" + "="*70)
    print("🧪 Testing OnlyOffice Integration")
    print("="*70)
    
    print("\n1️⃣ Checking OnlyOffice Document Server status...")
    try:
        response = requests.get('http://localhost:8080/healthcheck', timeout=2)
        if response.status_code == 200:
            print("   ✅ OnlyOffice is running!")
        else:
            print(f"   ⚠️  OnlyOffice returned status code {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ❌ OnlyOffice is not running!")
        print("   💡 Start it with: docker start onlyoffice-documentserver")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print("\n2️⃣ Checking Flask backend status...")
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=2)
        if response.status_code == 200:
            print("   ✅ Flask backend is running!")
        else:
            print(f"   ⚠️  Flask returned status code {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Flask backend is not running!")
        print("   💡 Start it with: python app.py")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print("\n3️⃣ Checking OnlyOffice status endpoint...")
    try:
        response = requests.get('http://localhost:5000/api/onlyoffice/status', timeout=2)
        data = response.json()
        if data.get('success'):
            print(f"   ✅ {data.get('message')}")
        else:
            print(f"   ⚠️  {data.get('message')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print("\n4️⃣ Checking if output directory exists...")
    import os
    output_dir = os.path.join(os.path.dirname(__file__), 'Backend', 'output')
    if os.path.exists(output_dir):
        files = [f for f in os.listdir(output_dir) if f.endswith('.docx')]
        print(f"   ✅ Output directory exists")
        print(f"   📁 Found {len(files)} .docx files")
        
        if files:
            print(f"\n5️⃣ Testing config endpoint with first file...")
            test_file = files[0]
            try:
                response = requests.get(f'http://localhost:5000/api/onlyoffice/config/{test_file}', timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Config endpoint working!")
                    
                    # Check if response has the expected structure
                    if 'config' in data and 'document' in data['config']:
                        document = data['config']['document']
                        print(f"   📄 Document: {document['title']}")
                        print(f"   🔑 Key: {document['key']}")
                        print(f"   📥 URL: {document['url']}")
                        print(f"   ✅ OnlyOffice config structure is correct!")
                    else:
                        print(f"   ⚠️  Unexpected response structure: {list(data.keys())}")
                else:
                    print(f"   ⚠️  Config endpoint returned {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        else:
            print(f"\n   💡 No .docx files found. Format a resume first to test the config endpoint.")
    else:
        print(f"   ⚠️  Output directory not found: {output_dir}")
    
    print("\n" + "="*70)
    print("✅ OnlyOffice Integration Test Complete!")
    print("="*70)
    print("\n📋 Next Steps:")
    print("   1. Create React component: src/components/OnlyOfficeEditor.jsx")
    print("   2. Add 'Edit in Browser' button to your results page")
    print("   3. Test the full flow: Format → Edit → Save")
    print("\n")
    
    return True

if __name__ == '__main__':
    test_onlyoffice_status()
