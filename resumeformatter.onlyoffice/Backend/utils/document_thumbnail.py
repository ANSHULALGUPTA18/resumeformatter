"""
Document Thumbnail Generator
Creates actual thumbnails from DOCX content using document conversion
"""

import os
import tempfile
import base64
from io import BytesIO

def create_document_thumbnail_fallback(template_name, template_id, output_path):
    """Create a more realistic document thumbnail with text lines"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create image with white background (document size ratio)
        img = Image.new('RGB', (300, 400), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw document shadow for depth
        draw.rectangle([12, 12, 292, 392], fill='#e0e0e0')
        
        # Draw main document
        draw.rectangle([10, 10, 290, 390], fill='white', outline='#c0c0c0', width=1)
        
        # Try to load a better font
        try:
            font_title = ImageFont.truetype("arial.ttf", 16)
            font_header = ImageFont.truetype("arial.ttf", 12)
            font_text = ImageFont.truetype("arial.ttf", 10)
            font_small = ImageFont.truetype("arial.ttf", 8)
        except:
            font_title = ImageFont.load_default()
            font_header = ImageFont.load_default()
            font_text = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Header area with name (like a resume header)
        draw.rectangle([20, 20, 280, 80], fill='#f8f9fa', outline='#dee2e6', width=1)
        
        # Large name at top
        draw.text((25, 25), "JOHN SMITH", fill='#1a1a1a', font=font_title)
        draw.text((25, 45), "Professional Resume", fill='#495057', font=font_text)
        draw.text((25, 60), "john.smith@email.com | (555) 123-4567", fill='#6c757d', font=font_small)
        
        # Simulate document content with text lines
        y_pos = 80
        
        # Contact section
        draw.text((25, y_pos), "CONTACT INFORMATION", fill='#495057', font=font_text)
        y_pos += 20
        for i in range(3):
            line_width = [120, 100, 140][i]
            draw.rectangle([25, y_pos, 25 + line_width, y_pos + 2], fill='#dee2e6')
            y_pos += 12
        
        y_pos += 15
        
        # Experience section
        draw.text((25, y_pos), "PROFESSIONAL EXPERIENCE", fill='#495057', font=font_text)
        y_pos += 20
        for i in range(4):
            line_width = [150, 180, 160, 140][i]
            draw.rectangle([25, y_pos, 25 + line_width, y_pos + 2], fill='#dee2e6')
            y_pos += 10
        
        y_pos += 15
        
        # Education section
        draw.text((25, y_pos), "EDUCATION", fill='#495057', font=font_text)
        y_pos += 20
        for i in range(2):
            line_width = [130, 170][i]
            draw.rectangle([25, y_pos, 25 + line_width, y_pos + 2], fill='#dee2e6')
            y_pos += 10
        
        y_pos += 15
        
        # Skills section
        draw.text((25, y_pos), "SKILLS", fill='#495057', font=font_text)
        y_pos += 20
        for i in range(3):
            line_width = [90, 110, 85][i]
            draw.rectangle([25, y_pos, 25 + line_width, y_pos + 2], fill='#dee2e6')
            y_pos += 10
        
        # Add a subtle watermark
        draw.text((220, 370), f"ID: {template_id[:8]}", fill='#adb5bd', font=font_text)
        
        # Save the thumbnail
        img.save(output_path, 'PNG', optimize=True, quality=90)
        return True
        
    except Exception as e:
        print(f"Failed to create document thumbnail: {e}")
        return False

def create_docx_preview_thumbnail(docx_path, output_path):
    """
    Create thumbnail from actual DOCX content using python-docx
    This reads the document structure and creates a visual representation
    """
    try:
        from docx import Document
        from PIL import Image, ImageDraw, ImageFont
        
        # Read the document
        doc = Document(docx_path)
        
        # Create image
        img = Image.new('RGB', (300, 400), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw border
        draw.rectangle([5, 5, 295, 395], outline='#d0d0d0', width=1)
        
        # Try to load fonts
        try:
            font_large = ImageFont.truetype("arial.ttf", 12)
            font_medium = ImageFont.truetype("arial.ttf", 10)
            font_small = ImageFont.truetype("arial.ttf", 8)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        y_pos = 15
        max_y = 380
        
        # Process document paragraphs
        for i, paragraph in enumerate(doc.paragraphs[:15]):  # Limit to first 15 paragraphs
            if y_pos >= max_y:
                break
                
            text = paragraph.text.strip()
            if not text:
                y_pos += 8  # Empty line spacing
                continue
            
            # Determine text style based on content and formatting
            if len(text) < 50 and (text.isupper() or any(word in text.upper() for word in ['EXPERIENCE', 'EDUCATION', 'SKILLS', 'CONTACT', 'SUMMARY', 'OBJECTIVE'])):
                # Section header
                font = font_medium
                color = '#2c3e50'
                y_pos += 5
            else:
                # Regular text
                font = font_small
                color = '#495057'
            
            # Truncate text to fit width
            max_chars = 35 if font == font_small else 25
            display_text = text[:max_chars] + "..." if len(text) > max_chars else text
            
            # Draw text
            draw.text((15, y_pos), display_text, fill=color, font=font)
            
            # Add line spacing
            y_pos += 15 if font == font_medium else 12
        
        # Add document info at bottom
        draw.text((15, 380), f"DOCX Template Preview", fill='#adb5bd', font=font_small)
        
        # Save thumbnail
        img.save(output_path, 'PNG', optimize=True, quality=90)
        return True
        
    except Exception as e:
        print(f"Failed to create DOCX preview thumbnail: {e}")
        return False

def save_placeholder_thumbnail(template_name, template_id, output_path):
    """
    Main function to create document thumbnails
    Tries multiple methods in order of preference
    """
    
    # Method 1: Try to create a realistic document preview
    if create_document_thumbnail_fallback(template_name, template_id, output_path):
        return True
    
    # Method 2: Fallback to simple thumbnail
    try:
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (300, 400), color='white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([10, 10, 290, 390], outline='#e0e0e0', width=2)
        draw.text((50, 200), f"Template: {template_name[:15]}", fill='#333333')
        img.save(output_path, 'PNG', optimize=True, quality=85)
        return True
    except:
        # Method 3: Ultra-minimal fallback
        png_data = base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=='
        )
        with open(output_path, 'wb') as f:
            f.write(png_data)
        return True
