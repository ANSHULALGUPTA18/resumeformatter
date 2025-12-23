"""
Advanced Resume OCR Package
Complete 7-layer OCR pipeline for reliable resume data extraction

Main Features:
- Visual layout analysis (detects columns, headings, zones)
- Multi-pass OCR (specialized passes for header/sections/body)
- Intelligent section identification (handles OCR errors)
- Content validation (prevents cross-section contamination)
- Enhanced header extraction (reliably finds candidate name)
- Template mapping (formats for any template)
- Post-processing (cleanup and quality scoring)

Quick Start:
    from ocr import process_resume_image

    result = process_resume_image("resume.png")
    print(f"Name: {result['candidate_info']['name']}")
    print(f"Email: {result['candidate_info']['email']}")
    print(f"Quality: {result['quality_scores']['overall']}")

Advanced Usage:
    from ocr import AdvancedResumeOCR

    processor = AdvancedResumeOCR(verbose=True)
    result = processor.process_resume("resume.png", template_path="template.docx")

    # Access detailed results
    header = result['candidate_info']
    sections = result['sections']
    quality = result['quality_scores']
    warnings = result['warnings']
"""

# Main exports
from .advanced_resume_ocr import (
    AdvancedResumeOCR,
    process_resume_image,
    process_resume_pdf,
    process_resume_docx,
    quick_extract
)

# Layer exports (for advanced usage)
from .visual_layout_analyzer import VisualLayoutAnalyzer
from .multipass_ocr_engine import MultiPassOCREngine
from .section_identifier import SectionIdentifier
from .content_validator import ContentValidator
from .header_extractor import HeaderExtractor
from .template_mapper import TemplateMapper
from .post_processor import PostProcessor

__version__ = '1.0.0'
__author__ = 'Resume Formatter Team'

__all__ = [
    # Main functions (most commonly used)
    'process_resume_image',
    'process_resume_pdf',
    'process_resume_docx',
    'quick_extract',

    # Advanced usage
    'AdvancedResumeOCR',

    # Individual layers (for custom pipelines)
    'VisualLayoutAnalyzer',
    'MultiPassOCREngine',
    'SectionIdentifier',
    'ContentValidator',
    'HeaderExtractor',
    'TemplateMapper',
    'PostProcessor',
]
