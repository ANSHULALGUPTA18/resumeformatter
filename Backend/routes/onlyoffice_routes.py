from flask import Blueprint, jsonify, request, send_file
import os
import uuid
from datetime import datetime
import requests
from config import Config

onlyoffice_bp = Blueprint('onlyoffice', __name__)

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
