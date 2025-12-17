from flask import Blueprint, jsonify, request, send_file
import os
import uuid
from datetime import datetime
import requests
from config import Config
from models.persistent_database import get_persistent_template_db
from models.database import TemplateDB

onlyoffice_bp = Blueprint('onlyoffice', __name__)

# Initialize database instances
persistent_db = get_persistent_template_db()
db = TemplateDB()

# Configuration - Use dynamic URLs from Config
ONLYOFFICE_URL = Config.ONLYOFFICE_URL
DOCUMENT_SERVER_URL = f"{ONLYOFFICE_URL}/web-apps/apps/api/documents/api.js"
OUTPUT_DIR = Config.OUTPUT_FOLDER

# Verify output directory exists
if not os.path.exists(OUTPUT_DIR):
    print(f"WARNING: Output directory does not exist: {OUTPUT_DIR}")
else:
    print(f"Output directory found: {OUTPUT_DIR}")

@onlyoffice_bp.route('/api/onlyoffice/config/<filename>', methods=['GET'])
def get_onlyoffice_config(filename):
    """Generate OnlyOffice editor configuration"""
    
    file_path = os.path.join(OUTPUT_DIR, filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    # Get file info
    file_size = os.path.getsize(file_path)
    file_ext = os.path.splitext(filename)[1][1:]  # Remove dot
    
    # Generate unique document key (required for OnlyOffice)
    # Use file modification time + filename for consistency
    file_mtime = os.path.getmtime(file_path)
    doc_key = f"{filename}_{int(file_mtime)}"
    
    # CRITICAL: Use host.docker.internal for Docker to reach Flask
    # This is the most reliable method for OnlyOffice container on Windows/Mac
    from config import Config
    backend_url = Config.BACKEND_URL
    
    print(f"✅ Using backend URL: {backend_url}")
    print(f"📡 OnlyOffice will use: {backend_url}")
    print(f"📡 Download URL: {backend_url}/api/onlyoffice/download/{filename}")
    print(f"📡 Callback URL: {backend_url}/api/onlyoffice/callback/{filename}")
    
    # OnlyOffice configuration
    editor_config = {
        "document": {
            "fileType": file_ext,
            "key": doc_key,
            "title": filename,
            "url": f"{backend_url}/api/onlyoffice/download/{filename}",
            "permissions": {
                "edit": True,
                "download": True,
                "print": True,
                "review": True
            }
        },
        "documentType": "word",
        "editorConfig": {
            "mode": "edit",
            "lang": "en",
            "callbackUrl": f"{backend_url}/api/onlyoffice/callback/{filename}",
            "user": {
                "id": "user-1",
                "name": "Resume Editor"
            },
            "customization": {
                "autosave": True,
                "forcesave": True,
                "comments": False,
                "chat": False,
                "compactHeader": False,
                "compactToolbar": False,
                "hideRightMenu": False,
                "toolbar": True,
                "statusBar": True,
                "leftMenu": True,
                "rightMenu": True,
                "features": {
                    "spellcheck": True
                }
            }
        },
        "width": "100%",
        "height": "100%"
    }
    
    print(f"✅ Config generated successfully for: {filename}")
    
    # Return with success flag
    return jsonify({
        'success': True,
        'config': editor_config
    })


@onlyoffice_bp.route('/api/onlyoffice/download/<filename>', methods=['GET'])
def download_document(filename):
    """Serve document file to OnlyOffice"""
    print(f"📥 OnlyOffice requesting download: {filename}")
    print(f"   Request from: {request.remote_addr}")
    print(f"   Request headers: {dict(request.headers)}")
    
    file_path = os.path.join(OUTPUT_DIR, filename)
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return jsonify({'error': 'File not found'}), 404
    
    print(f"✅ Serving file: {file_path} ({os.path.getsize(file_path)} bytes)")
    
    response = send_file(
        file_path,
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        as_attachment=False
    )
    
    # Add CORS headers for OnlyOffice
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    
    return response


@onlyoffice_bp.route('/api/onlyoffice/callback/<filename>', methods=['POST', 'OPTIONS'])
def save_callback(filename):
    """Handle save callback from OnlyOffice"""
    
    # Handle OPTIONS preflight request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    try:
        print(f"\n{'='*70}")
        print(f"📥 ONLYOFFICE CALLBACK RECEIVED")
        print(f"{'='*70}")
        print(f"   Filename: {filename}")
        print(f"   Method: {request.method}")
        print(f"   Remote IP: {request.remote_addr}")
        print(f"   Headers: {dict(request.headers)}")
        
        data = request.json
        print(f"   Data: {data}")
        
        # OnlyOffice sends status codes:
        # 1 = document is being edited
        # 2 = document is ready for saving
        # 3 = document saving error
        # 4 = document is closed with no changes
        # 6 = document is being edited, but the current document state is saved
        # 7 = error has occurred while force saving the document
        
        status = data.get('status')
        print(f"   Status: {status}")
        
        if status == 2 or status == 6:
            # Document is ready to be saved
            download_url = data.get('url')
            
            if download_url:
                print(f"   📥 Downloading edited document from: {download_url}")
                
                # Download the edited document
                response = requests.get(download_url, timeout=10)
                
                if response.status_code == 200:
                    # Save to output directory
                    file_path = os.path.join(OUTPUT_DIR, filename)
                    
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"   ✅ Document saved successfully: {filename} ({len(response.content)} bytes)")
                    print(f"{'='*70}\n")
                    
                    response = jsonify({'error': 0})
                    response.headers['Access-Control-Allow-Origin'] = '*'
                    return response
                else:
                    print(f"   ❌ Failed to download document: HTTP {response.status_code}")
                    print(f"{'='*70}\n")
                    return jsonify({'error': 1})
            else:
                print(f"   ⚠️  No download URL provided in callback")
                print(f"{'='*70}\n")
                return jsonify({'error': 1})
        
        # For other statuses, just acknowledge
        print(f"   ✅ Acknowledged status {status}")
        print(f"{'='*70}\n")
        
        response = jsonify({'error': 0})
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
        
    except Exception as e:
        print(f"   ❌ Callback error: {e}")
        import traceback
        traceback.print_exc()
        print(f"{'='*70}\n")
        
        response = jsonify({'error': 1})
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

@onlyoffice_bp.route('/api/onlyoffice/edit/<template_id>', methods=['GET'])
def edit_template(template_id):
    """Generate OnlyOffice configuration for editing a template"""
    try:
        print(f"\n{'='*70}")
        print(f"📝 OnlyOffice Template Edit Request")
        print(f"   Template ID: {template_id}")
        
        # Get template from database
        template = persistent_db.get_template(template_id)
        if not template:
            template = db.get_template(template_id)
        
        if not template:
            print(f"   ❌ Template not found")
            return jsonify({'success': False, 'message': 'Template not found'}), 404
        
        template_filename = template['filename']
        template_name = template['name']
        local_template_path = os.path.join(Config.TEMPLATE_FOLDER, template_filename)
        
        print(f"   Template: {template_name}")
        print(f"   File: {template_filename}")
        print(f"   Path: {local_template_path}")
        
        # Download from storage if not local
        if not os.path.exists(local_template_path):
            print(f"   📥 Downloading template from storage...")
            download_success = persistent_db.download_template_file(template_id, template_filename, local_template_path)
            if not download_success:
                print(f"   ❌ Failed to download template")
                return jsonify({'success': False, 'message': 'Template file not available'}), 404
        
        if not os.path.exists(local_template_path):
            print(f"   ❌ Template file not found")
            return jsonify({'success': False, 'message': 'Template file not found'}), 404
        
        # Generate unique document key
        file_mtime = os.path.getmtime(local_template_path)
        doc_key = f"template_{template_id}_{int(file_mtime)}"
        
        # Get file extension
        file_ext = os.path.splitext(template_filename)[1][1:]
        
        # Backend URL for callbacks
        backend_url = Config.BACKEND_URL
        
        print(f"   Document Key: {doc_key}")
        print(f"   Backend URL: {backend_url}")
        
        # OnlyOffice configuration
        editor_config = {
            "documentType": "word",
            "document": {
                "title": f"{template_name}.{file_ext}",
                "url": f"{backend_url}/api/onlyoffice/template-download/{template_id}",
                "fileType": file_ext,
                "key": doc_key,
                "permissions": {
                    "comment": True,
                    "copy": True,
                    "download": True,
                    "edit": True,
                    "fillForms": True,
                    "modifyContentControl": True,
                    "modifyFilter": True,
                    "print": True,
                    "review": True
                }
            },
            "editorConfig": {
                "mode": "edit",
                "lang": "en",
                "callbackUrl": f"{backend_url}/api/onlyoffice/template-callback/{template_id}",
                "user": {
                    "id": "user-1",
                    "name": "Template Editor"
                },
                "customization": {
                    "autosave": True,
                    "forcesave": True,
                    "comments": True,
                    "zoom": 100
                }
            },
            "width": "100%",
            "height": "100%",
            "type": "desktop"
        }
        
        print(f"   ✅ Configuration generated")
        print(f"{'='*70}\n")
        
        return jsonify(editor_config)
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print(f"{'='*70}\n")
        return jsonify({'success': False, 'message': str(e)}), 500

@onlyoffice_bp.route('/api/onlyoffice/template-download/<template_id>', methods=['GET'])
def download_template_for_editing(template_id):
    """Serve template file for OnlyOffice editing"""
    try:
        # Get template
        template = persistent_db.get_template(template_id)
        if not template:
            template = db.get_template(template_id)
        
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        template_filename = template['filename']
        local_template_path = os.path.join(Config.TEMPLATE_FOLDER, template_filename)
        
        # Download if not local
        if not os.path.exists(local_template_path):
            download_success = persistent_db.download_template_file(template_id, template_filename, local_template_path)
            if not download_success:
                return jsonify({'error': 'Template file not available'}), 404
        
        if not os.path.exists(local_template_path):
            return jsonify({'error': 'File not found'}), 404
        
        print(f"📤 Serving template for editing: {template_filename}")
        return send_file(local_template_path, as_attachment=False, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        
    except Exception as e:
        print(f"❌ Error serving template: {e}")
        return jsonify({'error': str(e)}), 500

@onlyoffice_bp.route('/api/onlyoffice/template-callback/<template_id>', methods=['POST', 'OPTIONS'])
def template_callback(template_id):
    """Handle OnlyOffice callback for template edits"""
    try:
        if request.method == 'OPTIONS':
            response = jsonify({'error': 0})
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            return response
        
        print(f"\n{'='*70}")
        print(f"📡 OnlyOffice Template Callback")
        print(f"   Template ID: {template_id}")
        
        data = request.json
        status = data.get('status')
        print(f"   Status: {status}")
        
        if status == 2 or status == 6:
            # Document ready to save
            download_url = data.get('url')
            
            if download_url:
                print(f"   📥 Downloading edited template...")
                
                # Download the edited document
                response = requests.get(download_url, timeout=10)
                
                if response.status_code == 200:
                    # Get template info
                    template = persistent_db.get_template(template_id)
                    if not template:
                        template = db.get_template(template_id)
                    
                    if template:
                        template_filename = template['filename']
                        local_template_path = os.path.join(Config.TEMPLATE_FOLDER, template_filename)
                        
                        # Save the edited template
                        with open(local_template_path, 'wb') as f:
                            f.write(response.content)
                        
                        print(f"   ✅ Template saved: {template_filename} ({len(response.content)} bytes)")
                        
                        # Re-extract CAI contact from edited template
                        try:
                            from utils.cai_contact_extractor import extract_cai_contact_from_template
                            cai_contact = extract_cai_contact_from_template(local_template_path)
                            if cai_contact:
                                print(f"   ✅ CAI Contact re-extracted from template:")
                                print(f"      Name: {cai_contact.get('name', 'N/A')}")
                                print(f"      State: {cai_contact.get('state', 'N/A')}")
                                # Update template with new CAI contact
                                persistent_db.update_template_cai_contact(template_id, cai_contact)
                            else:
                                print(f"   ⚠️  No CAI contact found in edited template")
                        except Exception as e:
                            print(f"   ⚠️  Failed to extract CAI contact: {e}")
                        
                        # Upload to persistent storage
                        try:
                            upload_success = persistent_db.upload_template_file(template_id, local_template_path)
                            if upload_success:
                                print(f"   ✅ Uploaded to persistent storage")
                        except Exception as e:
                            print(f"   ⚠️  Failed to upload to storage: {e}")
                        
                        print(f"{'='*70}\n")
                        
                        response = jsonify({'error': 0})
                        response.headers['Access-Control-Allow-Origin'] = '*'
                        return response
        
        # Acknowledge other statuses
        print(f"   ✅ Acknowledged status {status}")
        print(f"{'='*70}\n")
        
        response = jsonify({'error': 0})
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
        
    except Exception as e:
        print(f"   ❌ Callback error: {e}")
        import traceback
        traceback.print_exc()
        print(f"{'='*70}\n")
        
        response = jsonify({'error': 1})
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
