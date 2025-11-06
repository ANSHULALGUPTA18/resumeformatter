
# HYBRID PARSER INTEGRATION GUIDE
# ================================

## Step 1: Update app.py imports
Add this import at the top of app.py:

```python
# Enhanced parser with hybrid architecture
try:
    from utils.parse_resume_enhanced import parse_resume_enhanced
    ENHANCED_PARSER_AVAILABLE = True
except ImportError:
    from utils.advanced_resume_parser import ResumeParser
    ENHANCED_PARSER_AVAILABLE = False
```

## Step 2: Update the parse_resume function call
Replace existing parser calls with:

```python
if ENHANCED_PARSER_AVAILABLE:
    resume_data = parse_resume_enhanced(file_path, file_type)
else:
    # Fallback to existing parser
    parser = ResumeParser(file_path, file_type)
    resume_data = parser.parse()
```

## Step 3: Benefits
- Employment history section names preserved
- Education/certification deduplication
- Better section classification
- Automatic fallback to existing parser if hybrid fails

## Step 4: Testing
The hybrid parser fixes these issues:
1. Employment history section name removal
2. Education/certification content duplication
3. Section classification improvements

## Step 5: Configuration
You can configure the parser behavior in config.py:

```python
# Hybrid parser settings
USE_HYBRID_PARSER = True
ENABLE_ML_CLASSIFICATION = True
FALLBACK_TO_ADVANCED = True
```
