"""
Enhanced Resume Parser Integration
Provides hybrid parsing with fallback
"""


def parse_resume_enhanced(file_path, file_type):
    """Enhanced resume parsing with hybrid fallback"""
    try:
        from utils.hybrid_integration import parse_resume_with_hybrid_fallback
        return parse_resume_with_hybrid_fallback(file_path, file_type, use_hybrid=True)
    except Exception as e:
        # Fallback to existing parser
        from utils.advanced_resume_parser import ResumeParser
        parser = ResumeParser(file_path, file_type)
        return parser.parse()
