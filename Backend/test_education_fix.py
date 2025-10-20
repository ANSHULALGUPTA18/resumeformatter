"""Quick test to verify EDUCATION placeholder replacement and name bracketing"""
import os
import sys

# Test pywin32 availability
try:
    import win32com.client
    print("✅ pywin32 is available - COM post-processing will run")
    HAS_WIN32 = True
except ImportError:
    print("⚠️  pywin32 NOT available - install with: pip install pywin32")
    print("   COM post-processing (for shapes/text boxes) will be skipped")
    HAS_WIN32 = False

print("\n" + "="*70)
print("EDUCATION PLACEHOLDER & NAME BRACKETING TEST")
print("="*70)

# Sample resume data
test_data = {
    'name': 'Paula Lawson',
    'email': 'paula@example.com',
    'phone': '555-1234',
    'experience': [
        {
            'company': 'American Safety Institute (ASI) – Tallahassee, FL',
            'role': 'Florida Business Coordinator',
            'duration': 'Nov 2011-Sept 2025',
            'details': [
                'Oversaw operations for all ASI-affiliated driving schools in Florida, which collectively represented over 85% of the state's driver education market share.',
                'Acted as the primary liaison between ASI and Florida-based partners to ensure regulatory compliance, operational efficiency, and client satisfaction.',
            ]
        }
    ],
    'education': [
        {
            'degree': 'High School Graduation',
            'institution': '',
            'year': '1986',
            'details': []
        }
    ],
    'skills': ['QuickBooks', 'UPS WorldShip', 'Microsoft Office'],
    'sections': {
        'education': ['High School Graduation 1986']
    }
}

from models.database import TemplateDB
from config import Config
from utils.word_formatter import format_word_document

db = TemplateDB()
templates = db.get_all_templates()

if not templates:
    print("\n❌ No templates found!")
    sys.exit(1)

template = db.get_template(templates[0]['id'])
template_path = os.path.join(Config.TEMPLATE_FOLDER, template['filename'])

print(f"\n📄 Template: {template['name']}")
print(f"👤 Candidate: {test_data['name']}")
print(f"🎓 Education: {test_data['education']}")

template_analysis = {
    'template_path': template_path,
    'template_type': 'docx'
}

output_path = os.path.join(Config.OUTPUT_FOLDER, 'test_education_fix.docx')

print(f"\n🎯 Running formatter...\n")
print("="*70)

success = format_word_document(test_data, template_analysis, output_path)

print("="*70)

if success:
    print(f"\n✅ SUCCESS!")
    print(f"\n📁 Output: {output_path}")
    print(f"\n🔍 Check the output for:")
    print(f"   1. Right column EDUCATION should show education data (not placeholder)")
    print(f"   2. Candidate name should appear as: <Paula Lawson>")
    print(f"   3. Employment History should include the 'Oversaw operations...' bullet")
    
    if HAS_WIN32:
        print(f"\n✓ COM post-processing ran - shapes/text boxes were handled")
    else:
        print(f"\n⚠️  COM unavailable - if EDUCATION is in a text box, it won't be replaced")
        print(f"   Install pywin32: pip install pywin32")
else:
    print(f"\n❌ FAILED - check console output above")

print()
