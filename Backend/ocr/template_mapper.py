"""
LAYER 6: Template Mapper
Maps extracted resume sections to a template structure
- Analyzes template structure
- Maps sections to template placeholders
- Formats content according to template style
- Handles missing sections gracefully
"""

import re
from typing import Dict, List, Optional
from docx import Document


class TemplateMapper:
    """Maps extracted resume data to template format"""

    def __init__(self):
        pass

    def map_to_template(self, extracted_data: Dict, template_path: str = None) -> Dict:
        """
        Main method: Map extracted data to template structure

        Args:
            extracted_data: {
                'header': {...},
                'sections': {'EMPLOYMENT': [...], 'EDUCATION': [...], ...}
            }
            template_path: Optional path to template DOCX

        Returns:
            {
                'name': str,
                'email': str,
                'phone': str,
                'linkedin': str,
                'sections': {
                    'EMPLOYMENT': str,
                    'EDUCATION': str,
                    ...
                }
            }
        """
        print("\n  [Layer 6] Mapping to template structure...")

        # Extract header info
        header_info = extracted_data.get('header', {})

        # Extract sections
        sections = extracted_data.get('sections', {})

        # Format each section
        formatted_sections = {}
        for section_name, content_blocks in sections.items():
            formatted_content = self._format_section_content(section_name, content_blocks)
            if formatted_content:
                formatted_sections[section_name] = formatted_content
                print(f"    ✓ Formatted {section_name} ({len(content_blocks)} blocks)")

        return {
            'name': header_info.get('name', ''),
            'email': header_info.get('email', ''),
            'phone': header_info.get('phone', ''),
            'linkedin': header_info.get('linkedin', ''),
            'github': header_info.get('github', ''),
            'location': header_info.get('location', ''),
            'title': header_info.get('title', ''),
            'sections': formatted_sections
        }

    def _format_section_content(self, section_name: str, content_blocks: List[Dict]) -> str:
        """Format content blocks for a section"""
        if not content_blocks:
            return ''

        # Extract text from blocks (handle dict or string)
        texts = []
        for block in content_blocks:
            if isinstance(block, dict):
                text = block.get('text', '')
            else:
                text = str(block)

            if text and text.strip():
                texts.append(text.strip())

        if not texts:
            return ''

        # Format based on section type
        if section_name in ['EMPLOYMENT', 'EDUCATION', 'PROJECTS']:
            # Structured format with proper spacing
            return '\n\n'.join(texts)
        elif section_name == 'SKILLS':
            # Comma-separated or bulleted format
            combined = ' '.join(texts)
            # If already has structure, keep it
            if ',' in combined or '•' in combined:
                return combined
            else:
                # Otherwise, separate with commas
                return ', '.join(texts)
        elif section_name == 'SUMMARY':
            # Paragraph format
            return ' '.join(texts)
        else:
            # Default: line-separated
            return '\n'.join(texts)

    def analyze_template_structure(self, template_path: str) -> Dict:
        """
        Analyze template DOCX structure

        Returns:
            {
                'sections': ['EMPLOYMENT', 'EDUCATION', ...],
                'format_style': {...}
            }
        """
        try:
            doc = Document(template_path)
            sections = []

            for para in doc.paragraphs:
                text = para.text.strip().upper()

                # Check if this is a section heading
                if any(keyword in text for keyword in [
                    'EMPLOYMENT', 'EXPERIENCE', 'WORK',
                    'EDUCATION', 'ACADEMIC',
                    'SKILLS', 'COMPETENC',
                    'SUMMARY', 'PROFILE', 'OBJECTIVE',
                    'PROJECTS', 'CERTIFICATIONS', 'ACHIEVEMENTS'
                ]):
                    # Map to standard section name
                    if 'EMPLOY' in text or 'EXPERIENCE' in text or 'WORK' in text:
                        sections.append('EMPLOYMENT')
                    elif 'EDUCAT' in text or 'ACADEMIC' in text:
                        sections.append('EDUCATION')
                    elif 'SKILL' in text or 'COMPETENC' in text:
                        sections.append('SKILLS')
                    elif 'SUMMAR' in text or 'PROFILE' in text or 'OBJECTIVE' in text:
                        sections.append('SUMMARY')
                    elif 'PROJECT' in text:
                        sections.append('PROJECTS')
                    elif 'CERTIF' in text:
                        sections.append('CERTIFICATIONS')
                    elif 'ACHIEVE' in text or 'AWARD' in text:
                        sections.append('ACHIEVEMENTS')

            return {
                'sections': list(set(sections)),  # Remove duplicates
                'section_count': len(set(sections))
            }

        except Exception as e:
            print(f"    Warning: Could not analyze template: {e}")
            # Return default structure
            return {
                'sections': ['EMPLOYMENT', 'EDUCATION', 'SKILLS', 'SUMMARY'],
                'section_count': 4
            }

    def create_formatted_output(self, mapped_data: Dict) -> Dict:
        """
        Create final formatted output ready for template population

        Returns structured data for template rendering
        """
        return {
            'candidate_info': {
                'name': mapped_data.get('name', ''),
                'title': mapped_data.get('title', ''),
                'email': mapped_data.get('email', ''),
                'phone': mapped_data.get('phone', ''),
                'linkedin': mapped_data.get('linkedin', ''),
                'github': mapped_data.get('github', ''),
                'location': mapped_data.get('location', ''),
            },
            'sections': mapped_data.get('sections', {}),
            'metadata': {
                'extraction_method': 'OCR-MultiLayer',
                'sections_found': list(mapped_data.get('sections', {}).keys())
            }
        }


# Utility function
def map_extracted_to_template(extracted_data: Dict, template_path: str = None) -> Dict:
    """Convenience function to map extracted data to template"""
    mapper = TemplateMapper()
    mapped = mapper.map_to_template(extracted_data, template_path)
    return mapper.create_formatted_output(mapped)


if __name__ == "__main__":
    # Test with sample data
    sample_data = {
        'header': {
            'name': 'John Doe',
            'email': 'john.doe@email.com',
            'phone': '(555) 123-4567',
            'linkedin': 'linkedin.com/in/johndoe'
        },
        'sections': {
            'EMPLOYMENT': [
                {'text': 'Software Engineer at Google\n2020-2023\nDeveloped features...'}
            ],
            'EDUCATION': [
                {'text': 'Bachelor of Science in Computer Science\nMIT, 2020'}
            ],
            'SKILLS': [
                {'text': 'Python, Java, JavaScript, AWS, Docker'}
            ]
        }
    }

    result = map_extracted_to_template(sample_data)
    print("\nMapped output:")
    print(f"Name: {result['candidate_info']['name']}")
    print(f"Email: {result['candidate_info']['email']}")
    print(f"\nSections: {result['metadata']['sections_found']}")
