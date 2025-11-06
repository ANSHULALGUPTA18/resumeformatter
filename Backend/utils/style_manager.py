"""
Style Manager - Preserves and applies Word document formatting
Ensures alignment, fonts, colors, and styles are maintained during content replacement
"""
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import copy

class StyleManager:
    """Manages and preserves paragraph and run formatting in Word documents"""
    
    def __init__(self):
        self.style_cache = {}
    
    def capture_paragraph_style(self, paragraph, style_key=None):
        """
        Capture all formatting properties of a paragraph
        Returns a dictionary with all style properties
        """
        if not paragraph.runs:
            # If no runs, create default style
            style = {
                'alignment': paragraph.alignment,
                'space_before': paragraph.paragraph_format.space_before,
                'space_after': paragraph.paragraph_format.space_after,
                'line_spacing': paragraph.paragraph_format.line_spacing,
                'left_indent': paragraph.paragraph_format.left_indent,
                'right_indent': paragraph.paragraph_format.right_indent,
                'first_line_indent': paragraph.paragraph_format.first_line_indent,
                'keep_together': paragraph.paragraph_format.keep_together,
                'keep_with_next': paragraph.paragraph_format.keep_with_next,
                'runs': []
            }
        else:
            # Capture first run's font properties as default
            first_run = paragraph.runs[0]
            style = {
                'alignment': paragraph.alignment,
                'space_before': paragraph.paragraph_format.space_before,
                'space_after': paragraph.paragraph_format.space_after,
                'line_spacing': paragraph.paragraph_format.line_spacing,
                'left_indent': paragraph.paragraph_format.left_indent,
                'right_indent': paragraph.paragraph_format.right_indent,
                'first_line_indent': paragraph.paragraph_format.first_line_indent,
                'keep_together': paragraph.paragraph_format.keep_together,
                'keep_with_next': paragraph.paragraph_format.keep_with_next,
                'runs': []
            }
            
            # Capture each run's formatting
            for run in paragraph.runs:
                run_style = {
                    'font_name': run.font.name,
                    'font_size': run.font.size,
                    'bold': run.font.bold,
                    'italic': run.font.italic,
                    'underline': run.font.underline,
                    'color': run.font.color.rgb if run.font.color and run.font.color.rgb else None,
                    'all_caps': run.font.all_caps,
                    'small_caps': run.font.small_caps,
                    'strike': run.font.strike,
                    'superscript': run.font.superscript,
                    'subscript': run.font.subscript,
                }
                style['runs'].append(run_style)
        
        # Cache if key provided
        if style_key:
            self.style_cache[style_key] = style
        
        return style
    
    def apply_paragraph_style(self, paragraph, style):
        """
        Apply captured style to a paragraph
        Preserves all formatting properties
        """
        try:
            # Apply paragraph-level formatting
            if style.get('alignment') is not None:
                paragraph.alignment = style['alignment']
            
            pf = paragraph.paragraph_format
            if style.get('space_before') is not None:
                pf.space_before = style['space_before']
            if style.get('space_after') is not None:
                pf.space_after = style['space_after']
            if style.get('line_spacing') is not None:
                pf.line_spacing = style['line_spacing']
            if style.get('left_indent') is not None:
                pf.left_indent = style['left_indent']
            if style.get('right_indent') is not None:
                pf.right_indent = style['right_indent']
            if style.get('first_line_indent') is not None:
                pf.first_line_indent = style['first_line_indent']
            if style.get('keep_together') is not None:
                pf.keep_together = style['keep_together']
            if style.get('keep_with_next') is not None:
                pf.keep_with_next = style['keep_with_next']
            
            # Apply run-level formatting to all runs
            if style.get('runs') and len(style['runs']) > 0:
                # Use first run style as default for all runs
                default_run_style = style['runs'][0]
                
                for run in paragraph.runs:
                    self._apply_run_style(run, default_run_style)
        
        except Exception as e:
            print(f"  ⚠️  Error applying style: {e}")
    
    def _apply_run_style(self, run, run_style):
        """Apply formatting to a single run"""
        try:
            if run_style.get('font_name'):
                run.font.name = run_style['font_name']
            if run_style.get('font_size'):
                run.font.size = run_style['font_size']
            if run_style.get('bold') is not None:
                run.font.bold = run_style['bold']
            if run_style.get('italic') is not None:
                run.font.italic = run_style['italic']
            if run_style.get('underline') is not None:
                run.font.underline = run_style['underline']
            if run_style.get('color'):
                run.font.color.rgb = run_style['color']
            if run_style.get('all_caps') is not None:
                run.font.all_caps = run_style['all_caps']
            if run_style.get('small_caps') is not None:
                run.font.small_caps = run_style['small_caps']
            if run_style.get('strike') is not None:
                run.font.strike = run_style['strike']
            if run_style.get('superscript') is not None:
                run.font.superscript = run_style['superscript']
            if run_style.get('subscript') is not None:
                run.font.subscript = run_style['subscript']
        except Exception as e:
            print(f"    ⚠️  Error applying run style: {e}")
    
    def replace_text_preserve_style(self, paragraph, new_text):
        """
        Replace paragraph text while preserving all formatting
        This is the key function for maintaining styles during replacement
        """
        # Capture current style
        style = self.capture_paragraph_style(paragraph)
        
        # Clear paragraph and add new text
        paragraph.clear()
        run = paragraph.add_run(new_text)
        
        # Reapply style
        self.apply_paragraph_style(paragraph, style)
        
        return paragraph
    
    def get_cached_style(self, style_key):
        """Retrieve a cached style by key"""
        return self.style_cache.get(style_key)
    
    def cache_template_styles(self, doc):
        """
        Scan template and cache common section styles
        Returns a dictionary of section keys to styles
        """
        section_styles = {}
        
        # Common section keywords to look for
        section_keywords = {
            'name': ['<NAME>', '<CANDIDATE NAME>', 'NAME'],
            'summary': ['SUMMARY', 'PROFESSIONAL SUMMARY', 'PROFILE'],
            'employment': ['EMPLOYMENT HISTORY', 'WORK EXPERIENCE', 'EXPERIENCE'],
            'education': ['EDUCATION', 'ACADEMIC BACKGROUND'],
            'skills': ['SKILLS', 'TECHNICAL SKILLS', 'COMPETENCIES'],
            'certifications': ['CERTIFICATIONS', 'CERTIFICATES', 'LICENSES']
        }
        
        for para_idx, paragraph in enumerate(doc.paragraphs):
            text_upper = paragraph.text.strip().upper()
            
            # Check if this paragraph matches any section keyword
            for section_key, keywords in section_keywords.items():
                if any(kw in text_upper for kw in keywords):
                    style = self.capture_paragraph_style(paragraph)
                    section_styles[section_key] = style
                    print(f"  📋 Cached style for '{section_key}' from paragraph {para_idx}: {text_upper[:50]}")
                    break
        
        return section_styles
    
    def apply_section_style(self, paragraph, section_key):
        """Apply a cached section style to a paragraph"""
        style = self.get_cached_style(section_key)
        if style:
            self.apply_paragraph_style(paragraph, style)
            return True
        return False

# Global instance
style_manager = StyleManager()
