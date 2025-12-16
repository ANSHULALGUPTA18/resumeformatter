"""
Script to regenerate thumbnails for all existing templates
Run this after deploying the thumbnail fix to generate thumbnails for existing templates
"""

import os
import sys
import platform

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.persistent_database import get_persistent_template_db
from utils.azure_storage import get_storage_manager
from config import Config

def regenerate_thumbnails():
    """Regenerate thumbnails for all templates"""
    
    # Check if running on Windows (required for thumbnail generation)
    if platform.system().lower() != 'windows' or os.name != 'nt':
        print("❌ Thumbnail generation requires Windows")
        print("   This script must be run on a Windows machine with MS Word installed")
        return
    
    print("\n" + "="*70)
    print("🖼️  THUMBNAIL REGENERATION SCRIPT")
    print("="*70 + "\n")
    
    # Initialize storage
    persistent_db = get_persistent_template_db()
    storage_manager = get_storage_manager()
    
    # Ensure output folder exists
    os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)
    os.makedirs(Config.TEMPLATE_FOLDER, exist_ok=True)
    
    # Get all templates
    templates = persistent_db.get_all_templates()
    
    if not templates:
        print("ℹ️  No templates found in storage")
        return
    
    print(f"📋 Found {len(templates)} template(s)\n")
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for i, template in enumerate(templates, 1):
        template_id = template['id']
        template_name = template['name']
        filename = template['filename']
        
        print(f"[{i}/{len(templates)}] Processing: {template_name}")
        
        # Check if thumbnail already exists
        if storage_manager.thumbnail_exists(template_id):
            print(f"   ✓ Thumbnail already exists, skipping")
            skip_count += 1
            continue
        
        try:
            # Download template file
            temp_template_path = os.path.join(Config.TEMPLATE_FOLDER, filename)
            if not persistent_db.download_template_file(template_id, filename, temp_template_path):
                print(f"   ❌ Failed to download template file")
                error_count += 1
                continue
            
            # Generate thumbnail
            import pythoncom
            from docx2pdf import convert
            import fitz  # PyMuPDF
            from PIL import Image
            
            thumbnail_filename = f"{template_id}_thumb.png"
            thumbnail_path = os.path.join(Config.OUTPUT_FOLDER, thumbnail_filename)
            temp_pdf = os.path.join(Config.OUTPUT_FOLDER, f"{template_id}_temp.pdf")
            
            # Convert DOCX to PDF
            pythoncom.CoInitialize()
            try:
                convert(temp_template_path, temp_pdf)
            finally:
                pythoncom.CoUninitialize()
            
            # Convert first page to image
            if os.path.exists(temp_pdf):
                pdf_document = fitz.open(temp_pdf)
                first_page = pdf_document[0]
                pix = first_page.get_pixmap(matrix=fitz.Matrix(120/72, 120/72))
                
                temp_png = thumbnail_path.replace('.png', '_temp.png')
                pix.save(temp_png)
                pdf_document.close()
                
                # Optimize with PIL
                img = Image.open(temp_png)
                img.save(thumbnail_path, 'PNG', optimize=True, quality=85)
                
                # Clean up temp files
                os.remove(temp_pdf)
                os.remove(temp_png)
                os.remove(temp_template_path)
                
                # Upload to Azure Storage
                if storage_manager.upload_thumbnail(template_id, thumbnail_path):
                    print(f"   ✅ Thumbnail generated and uploaded")
                    success_count += 1
                    
                    # Clean up local thumbnail
                    try:
                        os.remove(thumbnail_path)
                    except:
                        pass
                else:
                    print(f"   ⚠️  Thumbnail generated but upload failed")
                    error_count += 1
            else:
                print(f"   ❌ PDF conversion failed")
                error_count += 1
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            error_count += 1
            # Clean up on error
            for cleanup_file in [temp_template_path, temp_pdf, thumbnail_path]:
                try:
                    if os.path.exists(cleanup_file):
                        os.remove(cleanup_file)
                except:
                    pass
    
    # Summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    print(f"✅ Successfully generated: {success_count}")
    print(f"⏭️  Skipped (already exist): {skip_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📋 Total templates: {len(templates)}")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        regenerate_thumbnails()
    except KeyboardInterrupt:
        print("\n\n⚠️  Script interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
