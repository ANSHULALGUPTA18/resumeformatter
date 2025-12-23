"""
ADVANCED RESUME OCR PROCESSOR
Main orchestrator that coordinates all 7 layers for reliable OCR-based resume extraction

Complete Pipeline:
    Layer 1: Visual Layout Analysis
    Layer 2: Multi-Pass OCR
    Layer 3: Section Identification
    Layer 4: Content Validation
    Layer 5: Header Extraction
    Layer 6: Template Mapping
    Layer 7: Post-Processing

Usage:
    from ocr.advanced_resume_ocr import process_resume_image

    result = process_resume_image("resume.png")
    print(f"Name: {result['candidate_info']['name']}")
    print(f"Quality: {result['quality_scores']['overall']}")
"""

import os
import time
from typing import Dict, Optional
from PIL import Image
import numpy as np

# Import all layers
from .visual_layout_analyzer import VisualLayoutAnalyzer
from .multipass_ocr_engine import MultiPassOCREngine
from .section_identifier import SectionIdentifier
from .content_validator import ContentValidator
from .header_extractor import HeaderExtractor
from .template_mapper import TemplateMapper
from .post_processor import PostProcessor
from .docx_image_extractor import docx_to_ocr_image, DOCXImageExtractor


class AdvancedResumeOCR:
    """
    Complete OCR pipeline for resume image processing
    Solves all major OCR issues:
    - Missing candidate names
    - Section misidentification
    - Cross-section contamination
    - Lost visual structure
    """

    def __init__(self, verbose: bool = True):
        """
        Initialize all processing layers

        Args:
            verbose: If True, print progress messages
        """
        self.verbose = verbose

        # Initialize all layers
        self.layout_analyzer = VisualLayoutAnalyzer()
        self.ocr_engine = MultiPassOCREngine()
        self.section_identifier = SectionIdentifier()
        self.content_validator = ContentValidator()
        self.header_extractor = HeaderExtractor()
        self.template_mapper = TemplateMapper()
        self.post_processor = PostProcessor()

    def process_resume(self, image_path: str, template_path: Optional[str] = None) -> Dict:
        """
        Main method: Process a resume image through complete pipeline

        Args:
            image_path: Path to resume image (PNG, JPG) or PDF page
            template_path: Optional path to template DOCX

        Returns:
            {
                'candidate_info': {name, email, phone, ...},
                'sections': {EMPLOYMENT: ..., EDUCATION: ..., ...},
                'quality_scores': {overall, name, contact, ...},
                'warnings': [...],
                'recommendations': [...],
                'processing_time': float
            }
        """
        start_time = time.time()

        if self.verbose:
            print("\n" + "="*70)
            print("ADVANCED RESUME OCR PROCESSING")
            print("="*70)
            print(f"Input: {os.path.basename(image_path) if isinstance(image_path, str) else 'Image object'}")

        try:
            # LAYER 1: Visual Layout Analysis
            if self.verbose:
                print("\n[Layer 1/7] Analyzing visual layout...")
            layout_info = self.layout_analyzer.analyze_layout(image_path)

            if self.verbose:
                print(f"  ✓ Found {len(layout_info['text_blocks'])} text blocks")
                print(f"  ✓ Detected {len(layout_info['headings'])} headings")
                print(f"  ✓ Layout: {layout_info['columns']['count']}-column")

            # LAYER 2: Multi-Pass OCR
            if self.verbose:
                print("\n[Layer 2/7] Performing multi-pass OCR...")
            ocr_results = self.ocr_engine.perform_multipass_ocr(image_path, layout_info)

            if self.verbose:
                print(f"  ✓ Header OCR: {ocr_results['header_ocr']['confidence']:.1f}% confidence")
                print(f"  ✓ Extracted {len(ocr_results['section_headers_ocr'])} section headers")
                print(f"  ✓ Extracted {len(ocr_results['body_ocr'])} content blocks")

            # LAYER 3: Section Identification
            if self.verbose:
                print("\n[Layer 3/7] Identifying sections...")
            identified_sections = self.section_identifier.identify_sections(ocr_results)

            if self.verbose:
                print(f"  ✓ Identified {len(identified_sections)} sections:")
                for section_name in identified_sections.keys():
                    print(f"    - {section_name}")

            # LAYER 4: Content Validation
            if self.verbose:
                print("\n[Layer 4/7] Validating content...")
            validated_sections = self.content_validator.validate_sections(identified_sections)

            # LAYER 5: Header Extraction
            if self.verbose:
                print("\n[Layer 5/7] Extracting header information...")
            header_info = self.header_extractor.extract_header_info(
                ocr_results['header_ocr'],
                layout_info
            )

            # LAYER 6: Template Mapping
            if self.verbose:
                print("\n[Layer 6/7] Mapping to template structure...")
            extracted_data = {
                'header': header_info,
                'sections': validated_sections
            }
            mapped_data = self.template_mapper.map_to_template(extracted_data, template_path)

            # LAYER 7: Post-Processing
            if self.verbose:
                print("\n[Layer 7/7] Post-processing and quality validation...")
            final_output = self.post_processor.process_final_output(mapped_data)

            # Add processing metadata
            processing_time = time.time() - start_time
            final_output['processing_time'] = processing_time
            final_output['pipeline_version'] = '1.0.0'

            if self.verbose:
                print("\n" + "="*70)
                print("PROCESSING COMPLETE")
                print("="*70)
                print(f"Time: {processing_time:.2f}s")
                print(f"Overall Quality: {final_output['quality_scores']['overall']:.1%}")
                print(f"Candidate: {final_output['candidate_info'].get('name', 'N/A')}")

                # Show quality report
                print("\n" + self.post_processor.generate_user_report(final_output))

            return final_output

        except Exception as e:
            error_msg = f"Error processing resume: {str(e)}"
            if self.verbose:
                print(f"\n❌ {error_msg}")
                import traceback
                traceback.print_exc()

            return {
                'success': False,
                'error': error_msg,
                'candidate_info': {},
                'sections': {},
                'quality_scores': {'overall': 0.0},
                'warnings': [error_msg],
                'recommendations': ['Please try manual data entry']
            }

    def process_pdf_resume(self, pdf_path: str, template_path: Optional[str] = None) -> Dict:
        """
        Process a PDF resume by converting to images first

        Args:
            pdf_path: Path to PDF file
            template_path: Optional template path

        Returns:
            Same as process_resume()
        """
        try:
            # Import PDF processing
            import fitz  # PyMuPDF

            # Open PDF
            doc = fitz.open(pdf_path)

            # Process first page (most resumes are 1 page)
            page = doc[0]

            # Convert to image
            pix = page.get_pixmap(dpi=300)  # High resolution for OCR
            img_data = pix.tobytes("png")

            # Convert to PIL Image
            from io import BytesIO
            pil_img = Image.open(BytesIO(img_data))

            # Process image
            return self.process_resume(pil_img, template_path)

        except ImportError:
            return {
                'success': False,
                'error': 'PyMuPDF not installed. Install with: pip install PyMuPDF',
                'warnings': ['Cannot process PDF files without PyMuPDF'],
                'recommendations': ['Install PyMuPDF or convert PDF to image first']
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error processing PDF: {str(e)}',
                'warnings': [str(e)],
                'recommendations': ['Try converting PDF to image manually']
            }

    def process_docx_resume(self, docx_path: str, template_path: Optional[str] = None) -> Dict:
        """
        Process a DOCX resume with embedded images

        Args:
            docx_path: Path to DOCX file
            template_path: Optional template path

        Returns:
            Same as process_resume()
        """
        try:
            print("\n" + "="*70)
            print("PROCESSING DOCX WITH EMBEDDED IMAGES")
            print("="*70)

            # Extract and combine images from DOCX
            combined_image = docx_to_ocr_image(docx_path)

            if not combined_image:
                # Fallback: try to extract text from DOCX
                print("[WARN] No images found, trying text extraction...")
                extractor = DOCXImageExtractor()
                text = extractor.extract_text_from_docx(docx_path)

                if text:
                    return {
                        'success': True,
                        'candidate_info': {'name': 'Unknown'},
                        'sections': {'RAW_TEXT': text},
                        'quality_scores': {'overall': 0.5},
                        'warnings': ['No images found in DOCX, extracted text only'],
                        'recommendations': ['Convert resume to image format for better OCR']
                    }
                else:
                    return {
                        'success': False,
                        'error': 'No images or text found in DOCX',
                        'warnings': ['DOCX appears to be empty'],
                        'recommendations': ['Please check the DOCX file']
                    }

            # Process the combined image
            print(f"[INFO] Processing combined image ({combined_image.size[0]}x{combined_image.size[1]})")
            return self.process_resume(combined_image, template_path)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': f'Error processing DOCX: {str(e)}',
                'warnings': [str(e)],
                'recommendations': ['Try converting DOCX to PDF or image first']
            }


# Convenience functions
def process_resume_image(image_path: str, template_path: Optional[str] = None, verbose: bool = True) -> Dict:
    """
    Convenience function: Process a resume image

    Args:
        image_path: Path to image file or PIL Image
        template_path: Optional template DOCX path
        verbose: Print progress

    Returns:
        Processed resume data with quality scores
    """
    processor = AdvancedResumeOCR(verbose=verbose)
    return processor.process_resume(image_path, template_path)


def process_resume_pdf(pdf_path: str, template_path: Optional[str] = None, verbose: bool = True) -> Dict:
    """
    Convenience function: Process a PDF resume

    Args:
        pdf_path: Path to PDF file
        template_path: Optional template DOCX path
        verbose: Print progress

    Returns:
        Processed resume data with quality scores
    """
    processor = AdvancedResumeOCR(verbose=verbose)
    return processor.process_pdf_resume(pdf_path, template_path)


def process_resume_docx(docx_path: str, template_path: Optional[str] = None, verbose: bool = True) -> Dict:
    """
    Convenience function: Process a DOCX resume with embedded images

    Args:
        docx_path: Path to DOCX file
        template_path: Optional template DOCX path
        verbose: Print progress

    Returns:
        Processed resume data with quality scores
    """
    processor = AdvancedResumeOCR(verbose=verbose)
    return processor.process_docx_resume(docx_path, template_path)


def quick_extract(image_path: str) -> Dict:
    """
    Quick extraction with minimal output

    Returns:
        {'name': str, 'email': str, 'phone': str, 'sections': {...}}
    """
    result = process_resume_image(image_path, verbose=False)

    return {
        'name': result['candidate_info'].get('name', ''),
        'email': result['candidate_info'].get('email', ''),
        'phone': result['candidate_info'].get('phone', ''),
        'sections': result.get('sections', {}),
        'quality': result['quality_scores']['overall']
    }


# Main entry point for testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python advanced_resume_ocr.py <image_path> [template_path]")
        print("\nExample:")
        print("  python advanced_resume_ocr.py resume.png")
        print("  python advanced_resume_ocr.py resume.pdf template.docx")
        sys.exit(1)

    image_path = sys.argv[1]
    template_path = sys.argv[2] if len(sys.argv) > 2 else None

    # Detect file type
    if image_path.lower().endswith('.pdf'):
        result = process_resume_pdf(image_path, template_path)
    else:
        result = process_resume_image(image_path, template_path)

    # Save result to JSON
    import json
    output_file = "ocr_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Results saved to: {output_file}")
