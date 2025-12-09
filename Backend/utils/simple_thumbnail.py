"""Simple thumbnail fallback"""
import os
import base64

def create_minimal_png(output_path):
    """Create a minimal PNG"""
    png_data = base64.b64decode(
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=='
    )
    with open(output_path, 'wb') as f:
        f.write(png_data)

def save_placeholder_thumbnail(template_name, template_id, output_path):
    """Save placeholder thumbnail"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGB', (300, 400), color='white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([2, 2, 298, 398], outline='#e0e0e0', width=2)
        doc_x, doc_y = 110, 80
        draw.rectangle([doc_x, doc_y, doc_x+80, doc_y+100], fill='#4a90e2', outline='#2c5aa0', width=2)
        draw.text((150, 220), template_name[:15], fill='#333333', anchor='mm')
        draw.text((150, 250), "Template", fill='#666666', anchor='mm')
        img.save(output_path, 'PNG', optimize=True, quality=85)
        return True
    except:
        create_minimal_png(output_path)
        return True