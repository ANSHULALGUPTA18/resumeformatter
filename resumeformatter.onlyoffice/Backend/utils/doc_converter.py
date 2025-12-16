"""
DOC to DOCX Converter Utility
Converts old .doc files to .docx format while preserving structure
"""

import os
import subprocess
import tempfile
from pathlib import Path

def convert_doc_to_docx(doc_file_path):
    """
    Convert a .doc file to .docx format while preserving structure
    
    Args:
        doc_file_path (str): Path to the .doc file
        
    Returns:
        str: Path to the converted .docx file, or None if conversion failed
    """
    try:
        # Check if the file exists and is a .doc file
        if not os.path.exists(doc_file_path):
            print(f"❌ File not found: {doc_file_path}")
            return None
            
        if not doc_file_path.lower().endswith('.doc'):
            print(f"❌ Not a .doc file: {doc_file_path}")
            return None
            
        # Create output path with .docx extension
        doc_path = Path(doc_file_path)
        docx_path = doc_path.with_suffix('.docx')
        
        print(f"🔄 Converting {doc_path.name} to {docx_path.name} (preserving structure)...")
        
        # Method 1: Try using LibreOffice (best for preserving structure)
        if _convert_with_libreoffice(doc_file_path, str(docx_path)):
            print(f"✅ Successfully converted using LibreOffice: {docx_path}")
            return str(docx_path)
            
        # Method 2: Try using pandoc (good structure preservation)
        if _convert_with_pandoc(doc_file_path, str(docx_path)):
            print(f"✅ Successfully converted using pandoc: {docx_path}")
            return str(docx_path)
            
        # Method 3: Try using unoconv (if available)
        if _convert_with_unoconv(doc_file_path, str(docx_path)):
            print(f"✅ Successfully converted using unoconv: {docx_path}")
            return str(docx_path)
            
        print(f"❌ All conversion methods failed for: {doc_file_path}")
        print(f"💡 Suggestion: Install LibreOffice in the container for better .doc support")
        return None
        
    except Exception as e:
        print(f"❌ Error converting {doc_file_path}: {str(e)}")
        return None

def _convert_with_libreoffice(doc_path, docx_path):
    """Try converting using LibreOffice headless mode"""
    try:
        # Try common LibreOffice paths
        libreoffice_paths = [
            'libreoffice',
            '/usr/bin/libreoffice',
            '/opt/libreoffice/program/soffice',
            'soffice'
        ]
        
        for lo_path in libreoffice_paths:
            try:
                # Create temp directory for output
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Run LibreOffice conversion
                    cmd = [
                        lo_path,
                        '--headless',
                        '--convert-to', 'docx',
                        '--outdir', temp_dir,
                        doc_path
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0:
                        # Find the converted file
                        doc_name = Path(doc_path).stem
                        temp_docx = os.path.join(temp_dir, f"{doc_name}.docx")
                        
                        if os.path.exists(temp_docx):
                            # Move to final location
                            os.rename(temp_docx, docx_path)
                            return True
                            
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
                continue
                
        return False
        
    except Exception:
        return False

def _convert_with_unoconv(doc_path, docx_path):
    """Try converting using unoconv (LibreOffice command-line tool)"""
    try:
        cmd = ['unoconv', '-f', 'docx', '-o', docx_path, doc_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and os.path.exists(docx_path):
            return True
            
        return False
        
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        return False

def _convert_with_pandoc(doc_path, docx_path):
    """Try converting using pandoc"""
    try:
        cmd = ['pandoc', '-f', 'doc', '-t', 'docx', '-o', docx_path, doc_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and os.path.exists(docx_path):
            return True
            
        return False
        
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        return False

def is_doc_file(filename):
    """Check if a file is a .doc file"""
    return filename.lower().endswith('.doc')

def needs_conversion(filename):
    """Check if a file needs conversion from .doc to .docx"""
    return is_doc_file(filename)
