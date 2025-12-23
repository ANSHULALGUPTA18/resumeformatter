# Advanced Resume OCR System

Complete 7-layer OCR pipeline that reliably extracts resume data from images and scanned PDFs.

## Problems Solved

✅ **Missing Candidate Names** - Multi-technique extraction (visual + NER + position)
✅ **Section Misidentification** - Fuzzy matching handles OCR errors like "EDUC4TION"
✅ **Cross-Section Contamination** - Independent validation prevents Education appearing in Skills
✅ **Lost Visual Structure** - Layout analysis preserves columns, headings, reading order
✅ **Noisy OCR Text** - Post-processing cleans artifacts and fixes common errors

## Installation

### Required Dependencies

```bash
pip install pytesseract opencv-python-headless Pillow
pip install fuzzywuzzy python-Levenshtein
pip install sentence-transformers spacy
python -m spacy download en_core_web_sm
```

### Tesseract OCR

Install Tesseract OCR engine:
- **Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki
- **Mac**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

## Quick Start

### Basic Usage

```python
from ocr import process_resume_image

# Process a resume image
result = process_resume_image("resume.png")

# Access extracted data
print(f"Name: {result['candidate_info']['name']}")
print(f"Email: {result['candidate_info']['email']}")
print(f"Phone: {result['candidate_info']['phone']}")

# Access sections
employment = result['sections'].get('EMPLOYMENT', '')
education = result['sections'].get('EDUCATION', '')
skills = result['sections'].get('SKILLS', '')

# Check quality
overall_quality = result['quality_scores']['overall']
if overall_quality > 0.8:
    print("High quality extraction!")
else:
    print(f"Warnings: {result['warnings']}")
```

### Process PDF Resume

```python
from ocr import process_resume_pdf

result = process_resume_pdf("resume.pdf")
```

### Quick Extraction (Minimal Output)

```python
from ocr import quick_extract

data = quick_extract("resume.png")
print(data['name'], data['email'], data['quality'])
```

## Architecture

### 7-Layer Processing Pipeline

```
Input: Resume Image/PDF
↓
[Layer 1] Visual Layout Analyzer
  → Detects zones, columns, headings, reading order
↓
[Layer 2] Multi-Pass OCR Engine
  → Pass 1: Header (name, contact)
  → Pass 2: Section headers
  → Pass 3: Body content
↓
[Layer 3] Section Identifier
  → Fuzzy matching for headers (handles OCR errors)
  → Content-based classification for headerless sections
↓
[Layer 4] Content Validator
  → Validates content matches section type
  → Detects and fixes cross-contamination
  → Moves misplaced content
↓
[Layer 5] Header Extractor
  → Extracts name (visual + NER + position)
  → Extracts contact info (email, phone, LinkedIn)
  → Fallback strategies
↓
[Layer 6] Template Mapper
  → Maps to template structure
  → Formats content appropriately
↓
[Layer 7] Post-Processor
  → Cleans OCR artifacts
  → Calculates quality scores
  → Generates warnings and recommendations
↓
Output: Structured Resume Data
```

## Advanced Usage

### Custom Pipeline

```python
from ocr import AdvancedResumeOCR

# Create processor with verbose output
processor = AdvancedResumeOCR(verbose=True)

# Process with template
result = processor.process_resume(
    image_path="resume.png",
    template_path="template.docx"
)

# Access detailed results
header = result['candidate_info']
sections = result['sections']
quality_scores = result['quality_scores']
warnings = result['warnings']
recommendations = result['recommendations']
processing_time = result['processing_time']
```

### Using Individual Layers

```python
from ocr import (
    VisualLayoutAnalyzer,
    MultiPassOCREngine,
    SectionIdentifier
)

# Layer 1: Analyze layout
analyzer = VisualLayoutAnalyzer()
layout = analyzer.analyze_layout("resume.png")

# Layer 2: Perform OCR
engine = MultiPassOCREngine()
ocr_results = engine.perform_multipass_ocr("resume.png", layout)

# Layer 3: Identify sections
identifier = SectionIdentifier()
sections = identifier.identify_sections(ocr_results)
```

## Output Format

```python
{
    'candidate_info': {
        'name': 'John Doe',
        'email': 'john.doe@email.com',
        'phone': '(555) 123-4567',
        'linkedin': 'linkedin.com/in/johndoe',
        'github': 'github.com/johndoe',
        'location': 'San Francisco, CA',
        'title': 'Senior Software Engineer'
    },
    'sections': {
        'EMPLOYMENT': 'Software Engineer at Google\n2020-2023\nDeveloped...',
        'EDUCATION': 'Bachelor of Science in Computer Science\nMIT, 2020',
        'SKILLS': 'Python, Java, JavaScript, AWS, Docker, React',
        'SUMMARY': 'Experienced software engineer with 5+ years...'
    },
    'quality_scores': {
        'overall': 0.92,
        'name': 0.95,
        'contact': 0.90,
        'employment': 0.90,
        'education': 0.88,
        'skills': 0.92
    },
    'completeness': {
        'name': True,
        'email': True,
        'phone': True,
        'employment': True,
        'education': True,
        'skills': True
    },
    'warnings': [],
    'recommendations': ['Please verify all sections for accuracy'],
    'processing_time': 3.45,
    'pipeline_version': '1.0.0'
}
```

## Integration with Resume Formatter

### Option 1: Update Existing Parser

```python
# In Backend/utils/resume_parser.py

from ocr import process_resume_image, process_resume_pdf

def parse_resume(file_path, file_type):
    """Enhanced parser with OCR support"""

    # Check if file is image or scanned PDF
    if file_type in ['png', 'jpg', 'jpeg']:
        # Use OCR directly
        ocr_result = process_resume_image(file_path)
        return format_ocr_result(ocr_result)

    elif file_type == 'pdf':
        # Try normal PDF text extraction first
        try:
            with pdfplumber.open(file_path) as pdf:
                text = pdf.pages[0].extract_text()

                # If text is minimal, use OCR
                if not text or len(text.strip()) < 100:
                    ocr_result = process_resume_pdf(file_path)
                    return format_ocr_result(ocr_result)
                else:
                    return parse_pdf_resume(file_path)
        except:
            # Fallback to OCR
            ocr_result = process_resume_pdf(file_path)
            return format_ocr_result(ocr_result)

    # Original DOCX handling
    return parse_word_resume(file_path)

def format_ocr_result(ocr_result):
    """Convert OCR result to resume_parser format"""
    return {
        'name': ocr_result['candidate_info']['name'],
        'email': ocr_result['candidate_info']['email'],
        'phone': ocr_result['candidate_info']['phone'],
        'linkedin': ocr_result['candidate_info'].get('linkedin', ''),
        'sections': ocr_result['sections'],
        'ocr_quality': ocr_result['quality_scores']['overall'],
        'warnings': ocr_result.get('warnings', [])
    }
```

### Option 2: API Endpoint

```python
# In Backend/app.py

from ocr import process_resume_image, process_resume_pdf

@app.route('/api/ocr-resume', methods=['POST'])
def ocr_resume():
    """Process resume image with advanced OCR"""

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    file_path = save_uploaded_file(file)

    try:
        # Detect file type
        if file.filename.lower().endswith('.pdf'):
            result = process_resume_pdf(file_path)
        else:
            result = process_resume_image(file_path)

        return jsonify({
            'success': True,
            'data': result,
            'message': 'Resume processed successfully'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
```

## Quality Scoring

The system provides detailed quality scores:

- **Overall**: 0.0-1.0 (weighted average of all fields)
- **Name**: Confidence in extracted name
- **Contact**: Based on email/phone/LinkedIn found
- **Employment**: Based on content length and structure
- **Education**: Based on content length and structure
- **Skills**: Based on content length and structure

### Quality Thresholds

- **≥ 0.8**: High quality, ready to use
- **0.6 - 0.8**: Medium quality, review recommended
- **< 0.6**: Low quality, manual review required

## Common Issues & Solutions

### Issue: Low Name Confidence

**Cause**: Name at top may be in unusual format or OCR quality poor
**Solution**: System uses fallback strategies (email prefix, first line)
**Action**: Verify name field if confidence < 0.7

### Issue: Section Mixing

**Cause**: OCR may group unrelated content together
**Solution**: Layer 4 validates and moves misplaced content automatically
**Action**: Review warnings for moved content

### Issue: Missing Contact Info

**Cause**: Contact info may be in image/logo or unusual format
**Solution**: Uses regex + NER for robust extraction
**Action**: Add contact info manually if missing

### Issue: Poor OCR Quality

**Cause**: Low resolution, skewed, or very noisy image
**Solution**: Multi-pass OCR with different preprocessing
**Action**: Use higher resolution scan (300+ DPI recommended)

## Testing

```bash
# Test individual modules
cd Backend/ocr
python visual_layout_analyzer.py resume.png
python multipass_ocr_engine.py resume.png
python advanced_resume_ocr.py resume.png

# Test with your resume
python advanced_resume_ocr.py path/to/resume.png

# Results saved to: ocr_result.json
```

## Performance

Typical processing times (on modern CPU):

- **Image Detection**: ~0.1s
- **Layout Analysis**: ~0.3s
- **Multi-Pass OCR**: ~2-4s
- **Section Processing**: ~0.5s
- **Total**: ~3-5s per resume

For scanned PDFs (300 DPI): ~5-8s per page

## Requirements

### Python Packages

```
pytesseract>=0.3.13
opencv-python-headless>=4.8.0
Pillow>=10.0.0
fuzzywuzzy>=0.18.0
python-Levenshtein>=0.21.0
sentence-transformers>=2.2.0
spacy>=3.7.0
python-docx>=1.0.0
PyMuPDF>=1.23.0 (optional, for PDF support)
```

### System Requirements

- **Tesseract OCR** 4.0+ installed
- **spaCy model**: en_core_web_sm
- **RAM**: 2GB+ (4GB recommended for ML models)
- **Disk**: ~3GB for ML models

## Troubleshooting

### Tesseract not found

```python
# In multipass_ocr_engine.py, update path:
pytesseract.pytesseract.tesseract_cmd = r"YOUR_PATH\tesseract.exe"
```

### spaCy model missing

```bash
python -m spacy download en_core_web_sm
```

### Out of memory

- Process resumes one at a time
- Use `quick_extract()` instead of full pipeline
- Reduce image resolution before processing

## Version History

### 1.0.0 (Current)

- ✅ Complete 7-layer pipeline
- ✅ Multi-pass OCR
- ✅ Content validation
- ✅ Quality scoring
- ✅ PDF support
- ✅ Template mapping

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review warnings and recommendations in output
3. Test with sample resumes first
4. Check Tesseract and spaCy installations

## License

Part of the Resume Formatter project.
