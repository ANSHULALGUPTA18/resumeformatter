from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import uuid
import os
import traceback
import json

from config import Config
from models.database import TemplateDB
from utils.advanced_template_analyzer import analyze_template
from utils.advanced_resume_parser import parse_resume

# Import routes
from routes.onlyoffice_routes import onlyoffice_bp
from routes.cai_contact_routes import cai_contact_bp

# Try to import enhanced formatter, fallback to standard if not available
try:
    from utils.enhanced_formatter_integration import format_resume_intelligent
    print("✅ Enhanced intelligent formatter loaded")
except ImportError:
    from utils.intelligent_formatter import format_resume_intelligent
    print("⚠️  Using standard formatter (enhanced version not available)")

app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)

# Enable CORS for React frontend and OnlyOffice Document Server
# CRITICAL: Must allow Docker container IPs for OnlyOffice callbacks
import socket

# Get local IP for CORS
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
except:
    local_ip = "192.168.0.104"

CORS(
    app,
    resources={r"/api/*": {
        "origins": [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "http://localhost:8080",  # OnlyOffice Document Server
            "http://host.docker.internal",  # Docker Desktop
            "http://host.docker.internal:5000",
            f"http://{local_ip}",  # Local network IP
            f"http://{local_ip}:5000",
            f"http://{local_ip}:3000",
            "http://192.168.65.254",  # Docker internal gateway
            "*"  # Allow all for OnlyOffice (it uses various IPs)
        ]
    }},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

# Register blueprints
app.register_blueprint(onlyoffice_bp)
app.register_blueprint(cai_contact_bp)

db = TemplateDB()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


# ===== Persistent CAI Contact storage used by both backend and formatter =====
def _cai_store_path():
    home = os.path.expanduser("~")
    return os.path.join(home, ".resume_formatter_cai_contact.json")


@app.route('/api/cai-contact', methods=['GET'])
def get_cai_contact():
    """Return stored CAI contact. If none, return empty fields."""
    path = _cai_store_path()
    data = {"name": "", "phone": "", "email": ""}
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                loaded = json.load(f) or {}
                data.update({k: loaded.get(k, "") for k in data.keys()})
    except Exception:
        pass
    return jsonify({"success": True, "contact": data})


@app.route('/api/cai-contact', methods=['POST'])
def save_cai_contact():
    """Persist CAI contact. Overwrites stored values. Body: JSON {name, phone, email}."""
    try:
        payload = request.get_json(silent=True) or {}
        data = {
            "name": str(payload.get("name", "")).strip(),
            "phone": str(payload.get("phone", "")).strip(),
            "email": str(payload.get("email", "")).strip(),
        }
        path = _cai_store_path()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return jsonify({"success": True, "contact": data})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Get all templates"""
    templates = db.get_all_templates()
    return jsonify({'success': True, 'templates': templates})

@app.route('/api/templates', methods=['POST'])
def upload_template():
    """Upload and analyze template"""
    try:
        if 'template_file' not in request.files or 'template_name' not in request.form:
            return jsonify({'success': False, 'message': 'Missing file or name'}), 400
        
        file = request.files['template_file']
        name = request.form['template_name'].strip()
        
        if file.filename == '' or not name:
            return jsonify({'success': False, 'message': 'Invalid input'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Invalid file type'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        file_type = filename.rsplit('.', 1)[1].lower()
        template_id = str(uuid.uuid4())
        saved_filename = f"{template_id}_{filename}"
        file_path = os.path.join(Config.TEMPLATE_FOLDER, saved_filename)
        file.save(file_path)
        
        print(f"\n{'='*70}")
        print(f"📤 UPLOADING TEMPLATE: {name}")
        print(f"{'='*70}\n")
        
        # Analyze template with advanced analyzer
        format_data = analyze_template(file_path)
        
        # Save to database
        db.add_template(template_id, name, saved_filename, file_type, format_data)
        
        return jsonify({
            'success': True,
            'id': template_id,
            'name': name,
            'message': 'Template uploaded and analyzed successfully'
        })
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/format', methods=['POST'])
def format_resumes():
    """Format resumes using selected template"""
    try:
        if 'template_id' not in request.form or 'resume_files' not in request.files:
            return jsonify({'success': False, 'message': 'Missing template or files'}), 400
        
        template_id = request.form['template_id']
        template = db.get_template(template_id)
        
        if not template:
            return jsonify({'success': False, 'message': 'Template not found'}), 404
        
        files = request.files.getlist('resume_files')
        formatted_files = []
        
        # Get template analysis
        template_analysis = template['format_data']
        
        # Ensure paths are set
        template_file_path = os.path.join(Config.TEMPLATE_FOLDER, template['filename'])
        template_analysis['template_path'] = template_file_path
        template_analysis['template_type'] = template['file_type']
        
        print(f"\n{'='*70}")
        print(f"🎯 FORMATTING SESSION")
        print(f"{'='*70}")
        print(f"📋 Template: {template['name']}")
        print(f"📁 Template Path: {template_file_path}")
        print(f"✓ Template Exists: {os.path.exists(template_file_path)}")
        print(f"📊 Resumes to Process: {len(files)}")
        print(f"{'='*70}\n")
        
        # Use ThreadPoolExecutor for parallel processing
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import time
        
        start_time = time.time()
        
        # Extract CAI contact data BEFORE threading (request context not available in threads)
        cai_contact_data = None
        cai_contacts_data = None
        edit_cai_contact = False
        
        # Check for multiple contacts first (new format)
        if 'cai_contacts' in request.form:
            try:
                import json
                cai_contacts_data = json.loads(request.form['cai_contacts'])
                edit_cai_contact = request.form.get('edit_cai_contact') == 'true'
                print(f"  ✏️  CAI Contacts (multiple) edit enabled: {len(cai_contacts_data)} contact(s)")
            except Exception as e:
                print(f"  ⚠️  Error parsing CAI contacts data: {e}")
        # Backward compatibility: single contact
        elif 'cai_contact' in request.form:
            try:
                import json
                cai_contact_data = json.loads(request.form['cai_contact'])
                edit_cai_contact = request.form.get('edit_cai_contact') == 'true'
                print(f"  ✏️  CAI Contact (single) edit enabled: {cai_contact_data}")
            except Exception as e:
                print(f"  ⚠️  Error parsing CAI contact data: {e}")
        
        def process_single_resume(file, idx, total, cai_data, cai_contacts, edit_cai):
            """Process a single resume file"""
            if file.filename == '' or not allowed_file(file.filename):
                return None
            
            # Save resume
            filename = secure_filename(file.filename)
            file_type = filename.rsplit('.', 1)[1].lower()
            resume_id = str(uuid.uuid4())
            saved_filename = f"{resume_id}_{filename}"
            file_path = os.path.join(Config.RESUME_FOLDER, saved_filename)
            file.save(file_path)
            
            print(f"\n{'─'*70}")
            print(f"📄 Processing Resume {idx}/{total}: {filename}")
            print(f"{'─'*70}")
            
            # Parse resume with advanced parser (with timing)
            parse_start = time.time()
            resume_data = parse_resume(file_path, file_type)
            parse_time = time.time() - parse_start
            print(f"  ⏱️  Parsing took: {parse_time:.2f}s")
            
            # Add CAI contact data if provided (multiple contacts preferred)
            if cai_contacts:
                resume_data['cai_contacts'] = cai_contacts
                resume_data['edit_cai_contact'] = edit_cai
            elif cai_data:
                resume_data['cai_contact'] = cai_data
                resume_data['edit_cai_contact'] = edit_cai
            
            if resume_data:
                # Format resume with intelligent formatter
                # Create DOCX only (NO PDF for speed!)
                docx_filename = f"formatted_{resume_id}.docx"
                docx_path = os.path.join(Config.OUTPUT_FOLDER, docx_filename)
                
                format_start = time.time()
                if format_resume_intelligent(resume_data, template_analysis, docx_path):
                    format_time = time.time() - format_start
                    print(f"  ⏱️  Formatting took: {format_time:.2f}s")
                    # Check if DOCX was created
                    if os.path.exists(docx_path):
                        # NO PDF CONVERSION FOR SPEED!
                        result = {
                            'filename': docx_filename,
                            'original': filename,
                            'name': resume_data['name'],
                            'template_name': template.get('name', 'resume')
                        }
                        print(f"✅ Successfully formatted: {filename} → {docx_filename}\n")
                        
                        # Cleanup
                        try:
                            os.remove(file_path)
                        except:
                            pass
                        
                        return result
                    else:
                        print(f"⚠️  Formatting completed but output file not found\n")
                else:
                    print(f"❌ Failed to format: {filename}\n")
            else:
                print(f"❌ Failed to parse resume: {filename}\n")
            
            # Cleanup on failure
            try:
                os.remove(file_path)
            except:
                pass
            
            return None
        
        # Process all resumes in parallel for speed
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        with ThreadPoolExecutor(max_workers=min(4, len(files))) as executor:
            # Submit all tasks with CAI contact data (single or multiple)
            future_to_file = {
                executor.submit(process_single_resume, file, idx, len(files), cai_contact_data, cai_contacts_data, edit_cai_contact): file 
                for idx, file in enumerate(files, 1)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_file):
                result = future.result()
                if result:
                    formatted_files.append(result)
        
        elapsed_time = time.time() - start_time
        print(f"{'='*70}")
        print(f"✅ FORMATTING COMPLETE: {len(formatted_files)}/{len(files)} successful")
        print(f"⏱️  Total Time: {elapsed_time:.2f} seconds ({elapsed_time/len(files):.2f}s per resume)")
        print(f"{'='*70}\n")
        
        return jsonify({
            'success': True,
            'files': formatted_files,
            'message': f'Formatted {len(formatted_files)} resume(s)'
        })
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    """Download formatted resume with proper filename"""
    file_path = os.path.join(Config.OUTPUT_FOLDER, filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    # Try to get a better filename from request args
    candidate_name = request.args.get('name', '')
    template_name = request.args.get('template', 'resume')
    
    # Clean names for filename
    if candidate_name:
        # Remove special characters and spaces
        clean_name = ''.join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in candidate_name)
        clean_name = clean_name.replace(' ', '_')
        clean_template = ''.join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in template_name)
        clean_template = clean_template.replace(' ', '_')
        download_name = f"{clean_name}_{clean_template}.docx"
    else:
        download_name = filename
    
    return send_from_directory(
        Config.OUTPUT_FOLDER, 
        filename, 
        as_attachment=True,
        download_name=download_name
    )

@app.route('/api/preview/<filename>')
def preview_file(filename):
    """Convert DOCX to HTML for fast preview - no PDF needed"""
    try:
        # Security: validate filename
        if '..' in filename or '/' in filename or '\\' in filename:
            return jsonify({'success': False, 'error': 'Invalid filename'}), 400
        
        # Handle both .docx and .pdf requests (convert .pdf to .docx)
        if filename.endswith('.pdf'):
            filename = filename.replace('.pdf', '.docx')
        
        # Look for DOCX file in output directory
        docx_path = os.path.join(Config.OUTPUT_FOLDER, filename)
        
        if not os.path.exists(docx_path):
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        # Convert DOCX to HTML using mammoth (fast!)
        try:
            import mammoth
        except ImportError:
            return jsonify({
                'success': False, 
                'error': 'mammoth library not installed. Run: pip install mammoth'
            }), 500
        
        print(f"📄 Converting DOCX to HTML preview: {filename}")
        with open(docx_path, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file)
            html_body = result.value
        
        # Wrap HTML with proper styling for resume display
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: 'Calibri', 'Arial', sans-serif;
            font-size: 11pt;
            line-height: 1.4;
            max-width: 850px;
            margin: 20px auto;
            padding: 20px;
            background: white;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 10px 0;
        }}
        td, th {{
            border: 1px solid #333;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f0f0f0;
            font-weight: bold;
        }}
        h1, h2, h3 {{
            color: #333;
            margin-top: 15px;
            margin-bottom: 10px;
        }}
        ul, ol {{
            margin-left: 20px;
        }}
        p {{
            margin: 5px 0;
        }}
    </style>
</head>
<body>
{html_body}
</body>
</html>
"""
        
        print(f"✅ HTML preview generated ({len(html_content)} chars)")
        return jsonify({
            'success': True,
            'html': html_content,
            'filename': filename
        })
        
    except Exception as e:
        print(f"❌ Preview error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/templates/<template_id>/thumbnail')
def get_template_thumbnail(template_id):
    """Generate and return template thumbnail image with caching"""
    try:
        template = db.get_template(template_id)
        if not template:
            return jsonify({'success': False, 'message': 'Template not found'}), 404
        
        file_path = os.path.join(Config.TEMPLATE_FOLDER, template['filename'])
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'message': 'Template file not found'}), 404
        
        # Generate thumbnail (convert first page to image)
        thumbnail_filename = f"{template_id}_thumb.png"
        thumbnail_path = os.path.join(Config.OUTPUT_FOLDER, thumbnail_filename)
        
        # Check if thumbnail already exists
        if not os.path.exists(thumbnail_path):
            try:
                import pythoncom
                from docx2pdf import convert
                import fitz  # PyMuPDF for PDF to image conversion
                from PIL import Image
                
                # Convert DOCX to PDF first
                temp_pdf = os.path.join(Config.OUTPUT_FOLDER, f"{template_id}_temp.pdf")
                
                pythoncom.CoInitialize()
                try:
                    convert(file_path, temp_pdf)
                finally:
                    pythoncom.CoUninitialize()
                
                # Convert first page of PDF to image
                if os.path.exists(temp_pdf):
                    pdf_document = fitz.open(temp_pdf)
                    first_page = pdf_document[0]
                    # Render at 120 DPI for faster loading (reduced from 150)
                    pix = first_page.get_pixmap(matrix=fitz.Matrix(120/72, 120/72))
                    
                    # Save as PNG first
                    temp_png = thumbnail_path.replace('.png', '_temp.png')
                    pix.save(temp_png)
                    pdf_document.close()
                    
                    # Optimize with PIL for smaller file size
                    img = Image.open(temp_png)
                    img.save(thumbnail_path, 'PNG', optimize=True, quality=85)
                    
                    # Clean up temp files
                    os.remove(temp_pdf)
                    os.remove(temp_png)
                else:
                    return jsonify({'success': False, 'message': 'PDF conversion failed'}), 500
                    
            except Exception as e:
                print(f"⚠️  Thumbnail generation failed: {e}")
                traceback.print_exc()
                return jsonify({'success': False, 'message': f'Thumbnail generation failed: {str(e)}'}), 500
        
        # Return the thumbnail image with aggressive caching
        response = send_from_directory(Config.OUTPUT_FOLDER, thumbnail_filename, mimetype='image/png')
        response.headers['Cache-Control'] = 'public, max-age=86400, immutable'  # Cache for 24 hours
        response.headers['ETag'] = template_id  # Use template ID as ETag
        return response
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/templates/<template_id>', methods=['DELETE'])
def delete_template(template_id):
    """Delete template"""
    try:
        template = db.get_template(template_id)
        if template:
            file_path = os.path.join(Config.TEMPLATE_FOLDER, template['filename'])
            if os.path.exists(file_path):
                os.remove(file_path)
            db.delete_template(template_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/onlyoffice/status', methods=['GET'])
def onlyoffice_status():
    """Check OnlyOffice Document Server status"""
    try:
        import requests
        response = requests.get('http://localhost:8080/healthcheck', timeout=2)
        if response.status_code == 200:
            return jsonify({
                'success': True,
                'status': 'running',
                'message': 'OnlyOffice Document Server is running'
            })
        else:
            return jsonify({
                'success': False,
                'status': 'error',
                'message': f'OnlyOffice returned status code {response.status_code}'
            })
    except requests.exceptions.ConnectionError:
        return jsonify({
            'success': False,
            'status': 'offline',
            'message': 'OnlyOffice Document Server is not running. Start it with: docker start onlyoffice-documentserver'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'error',
            'message': str(e)
        })

if __name__ == '__main__':
    # PRE-WARM ML MODELS FOR INSTANT FIRST REQUEST 
    # Disabled for faster startup - models will load on first request
    # try:
    #     from utils.model_cache import prewarm_models
    #     prewarm_models()
    # except Exception as e:
    #     print(f"  Model pre-warming failed: {e}")
    #     print("   Models will load on first request instead")
    print("⚡ Quick startup mode: ML models will load on first request")
    
    import socket
    
    # Get local IP for display
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "localhost"
    
    print("\n" + "="*70)
    print("🎯 RESUME FORMATTER - BACKEND SERVER")
    print("="*70)
    print("✅ API running on http://127.0.0.1:5000")
    print(f"✅ Network access: http://{local_ip}:5000")
    print("✅ React frontend: http://localhost:3000")
    print("✅ OnlyOffice Document Server: http://localhost:8080")
    print("="*70)
    print("📝 OnlyOffice Editor Routes:")
    print("   • /api/onlyoffice/config/<filename>")
    print("   • /api/onlyoffice/download/<filename>")
    print("   • /api/onlyoffice/callback/<filename>")
    print("="*70 + "\n")
    # CRITICAL: Bind to 0.0.0.0 to accept connections from Docker
    # Run without debug mode to avoid reloader issues
    app.run(debug=False, host='0.0.0.0', port=5000)
