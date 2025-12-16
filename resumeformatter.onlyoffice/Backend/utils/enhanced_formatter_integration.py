"""
Enhanced Formatter Integration
Integrates the enhanced section classifier with the existing formatting pipeline
"""

import os
from typing import Dict, Optional, List

# Comprehensive section synonym mapping for normalization
SECTION_SYNONYMS = {
    "summary": ["professional summary", "profile", "profile summary", "career objective", 
                "about me", "professional profile", "career summary", "objective"],
    "employment history": ["work experience", "experience", "career history", 
                          "professional experience", "employment", "work history",
                          "professional background", "job history"],
    "education": ["academic background", "qualifications", "academics", "studies", 
                 "schooling", "educational background", "degrees"],
    "skills": ["technical skills", "core competencies", "expertise", "abilities", 
              "tools", "skill set", "competencies", "technical competencies"],
    "certifications": ["courses", "licenses", "trainings", "certificates", 
                      "achievements", "credentials", "professional certifications"],
    "projects": ["portfolio", "case studies", "research work", "work samples",
                "key projects", "project experience"],
}

def normalize_heading(heading: str) -> str:
    """
    Normalize section heading to canonical form using synonym mapping
    
    Args:
        heading: Original section heading
        
    Returns:
        Normalized canonical section name
    """
    if not heading:
        return ""
    
    h = heading.strip().lower()
    
    # Check for exact or partial matches
    for canonical, synonyms in SECTION_SYNONYMS.items():
        if h == canonical:
            return canonical
        if any(syn in h or h in syn for syn in synonyms):
            return canonical
    
    return h


def validate_section_by_content(content: str) -> Optional[str]:
    """
    Validate and correct section classification using keyword-based content analysis
    
    Args:
        content: Section content text
        
    Returns:
        Corrected section name if confident, None otherwise
    """
    if not content or not isinstance(content, str):
        return None
    
    c_lower = content.lower()
    
    # Education indicators (highest priority - very specific)
    education_keywords = ["university", "degree", "bachelor", "master", "b.tech", "m.tech",
                         "school", "college", "graduated", "gpa", "phd", "doctorate"]
    if sum(1 for kw in education_keywords if kw in c_lower) >= 2:
        return "education"
    
    # Certification indicators (specific patterns)
    cert_keywords = ["certified", "certificate", "certification", "license", "credential",
                    "pmp", "safe", "scrum master", "aws certified", "cisco"]
    cert_patterns = ["project management professional", "certified safe", "scrum master"]
    if (sum(1 for kw in cert_keywords if kw in c_lower) >= 1 or
        any(pattern in c_lower for pattern in cert_patterns)):
        # But check it's not employment history (certifications are usually short)
        if len(content) < 500 and "worked" not in c_lower and "managed" not in c_lower:
            return "certifications"
    
    # Employment history indicators (job descriptions)
    employment_keywords = ["worked", "managed", "led", "developed", "responsible",
                          "collaborated", "provided", "established", "coordinated",
                          "implemented", "demonstrated"]
    employment_patterns = [r"\d{4}\s*[-–]\s*\d{4}", r"\d{1,2}/\d{4}", 
                          "project manager", "technical manager", "consultant"]
    if sum(1 for kw in employment_keywords if kw in c_lower) >= 3:
        return "employment history"
    
    # Skills indicators (tools and technologies)
    skills_keywords = ["python", "java", "javascript", "react", "sql", "aws", "azure",
                      "jira", "agile", "scrum", "tools", "technologies", "proficient"]
    if sum(1 for kw in skills_keywords if kw in c_lower) >= 3:
        # But check it's not a job description mentioning these
        if len(content) < 800 and "worked" not in c_lower:
            return "skills"
    
    return None


try:
    from utils.enhanced_section_classifier import get_section_classifier
    ENHANCED_CLASSIFIER_AVAILABLE = True
except ImportError:
    ENHANCED_CLASSIFIER_AVAILABLE = False
    print("⚠️  Enhanced classifier not available")

try:
    from utils.word_formatter import format_word_document
    WORD_FORMATTER_AVAILABLE = True
except ImportError:
    WORD_FORMATTER_AVAILABLE = False
    print("⚠️  Word formatter not available")


def enhance_resume_data_with_intelligent_mapping(resume_data: Dict, template_analysis: Dict, 
                                                  confidence_threshold: float = 0.6) -> Dict:
    """
    Enhance resume data with intelligent section mapping
    
    Args:
        resume_data: Parsed resume data from advanced_resume_parser
        template_analysis: Template analysis from advanced_template_analyzer
        confidence_threshold: Minimum confidence for classification (0-1)
        
    Returns:
        Enhanced resume data with better section mappings
    """
    if not ENHANCED_CLASSIFIER_AVAILABLE:
        print("⚠️  Enhanced classifier not available, using original data")
        return resume_data
    
    print(f"\n{'='*70}")
    print(f"🧠 INTELLIGENT SECTION MAPPING")
    print(f"{'='*70}\n")
    
    try:
        classifier = get_section_classifier(confidence_threshold)
        
        # Extract sections from resume_data
        sections_to_classify = []
        
        # Get sections from resume_data (if available)
        if 'sections' in resume_data and resume_data['sections']:
            for section_name, section_content in resume_data['sections'].items():
                # Handle both string and list content
                if isinstance(section_content, list):
                    content_str = '\n'.join(str(item) for item in section_content if item)
                else:
                    content_str = str(section_content) if section_content else ''
                
                if content_str and content_str.strip():
                    # Normalize heading using synonym mapping
                    normalized_heading = normalize_heading(section_name)
                    
                    sections_to_classify.append({
                        'heading': normalized_heading,
                        'original_heading': section_name,  # Keep original for reference
                        'content': content_str,
                        'position': len(sections_to_classify)
                    })
        
        # Also add structured data as sections
        position = len(sections_to_classify)
        
        if resume_data.get('summary'):
            sections_to_classify.append({
                'heading': 'Summary',
                'content': resume_data['summary'],
                'position': position
            })
            position += 1
        
        if resume_data.get('experience'):
            exp_content = '\n\n'.join([
                f"{exp.get('role', '')} at {exp.get('company', '')} ({exp.get('duration', '')})\n{exp.get('responsibilities', '')}"
                for exp in resume_data['experience']
            ])
            if exp_content.strip():
                sections_to_classify.append({
                    'heading': 'Experience',
                    'content': exp_content,
                    'position': position
                })
                position += 1
        
        if resume_data.get('education'):
            edu_content = '\n\n'.join([
                f"{edu.get('degree', '')} from {edu.get('institution', '')} ({edu.get('year', '')})"
                for edu in resume_data['education']
            ])
            if edu_content.strip():
                sections_to_classify.append({
                    'heading': 'Education',
                    'content': edu_content,
                    'position': position
                })
                position += 1
        
        if resume_data.get('skills'):
            if isinstance(resume_data['skills'], dict):
                skills_content = '\n'.join([
                    f"{category}: {', '.join(skills)}"
                    for category, skills in resume_data['skills'].items()
                ])
            elif isinstance(resume_data['skills'], list):
                skills_content = ', '.join(resume_data['skills'])
            else:
                skills_content = str(resume_data['skills'])
            
            if skills_content.strip():
                sections_to_classify.append({
                    'heading': 'Skills',
                    'content': skills_content,
                    'position': position
                })
                position += 1
        
        if resume_data.get('certifications'):
            # Handle both list and string
            if isinstance(resume_data['certifications'], list):
                cert_content = '\n'.join(str(c) for c in resume_data['certifications'] if c)
            else:
                cert_content = str(resume_data['certifications'])
            
            if cert_content.strip():
                sections_to_classify.append({
                    'heading': 'Certifications',
                    'content': cert_content,
                    'position': position
                })
                position += 1
        
        if resume_data.get('projects'):
            if isinstance(resume_data['projects'], list):
                proj_content = '\n\n'.join([
                    f"{proj.get('name', '') if isinstance(proj, dict) else str(proj)}: {proj.get('description', '') if isinstance(proj, dict) else ''}"
                    for proj in resume_data['projects']
                ])
            else:
                proj_content = str(resume_data['projects'])
            
            if proj_content.strip():
                sections_to_classify.append({
                    'heading': 'Projects',
                    'content': proj_content,
                    'position': position
                })
        
        # Get template sections
        template_sections_raw = template_analysis.get('sections', [])
        
        # Extract section names (handle both list of strings and list of dicts)
        template_sections = []
        if template_sections_raw:
            for section in template_sections_raw:
                if isinstance(section, dict):
                    # Extract 'name' or 'heading' field from dict
                    section_name = section.get('name') or section.get('heading') or section.get('title')
                    if section_name:
                        template_sections.append(section_name)
                elif isinstance(section, str):
                    template_sections.append(section)
        
        if not template_sections:
            # Fallback to common sections
            template_sections = [
                'SUMMARY', 'EMPLOYMENT HISTORY', 'EDUCATION', 
                'SKILLS', 'CERTIFICATIONS', 'PROJECTS'
            ]
        
        print(f"📋 Template sections: {', '.join(template_sections)}")
        print(f"📄 Candidate sections to classify: {len(sections_to_classify)}\n")
        
        # Classify sections
        if sections_to_classify:
            mapped_sections = classifier.batch_classify(sections_to_classify, template_sections)
            
            # Update resume_data with mapped sections
            if mapped_sections:
                if 'sections' not in resume_data:
                    resume_data['sections'] = {}
                
                # Merge mapped sections with content validation and smart merging
                print(f"\n📊 SECTION REMAPPING WITH VALIDATION:")
                
                for template_section, content in mapped_sections.items():
                    if template_section == '_uncertain':
                        continue
                    
                    # Validate classification using content analysis
                    validated_section = validate_section_by_content(content)
                    
                    if validated_section:
                        # Content validation suggests different section
                        # Find matching template section
                        final_section = None
                        for ts in template_sections:
                            if validated_section in ts.lower() or ts.lower() in validated_section:
                                final_section = ts
                                break
                        
                        if final_section and final_section != template_section:
                            print(f"   🔄 Content validation: '{template_section}' → '{final_section}'")
                            template_section = final_section
                    
                    # Smart merging: append if section already exists, don't overwrite
                    content_preview = content[:100] if isinstance(content, str) else str(content)[:100]
                    
                    if template_section in resume_data['sections']:
                        # Section already exists - append content
                        existing = resume_data['sections'][template_section]
                        if isinstance(existing, str) and isinstance(content, str):
                            resume_data['sections'][template_section] = existing + "\n\n" + content
                            print(f"   ➕ {template_section}: MERGED with existing content")
                        else:
                            resume_data['sections'][template_section] = content
                            print(f"   ⚠️  {template_section}: REPLACED (type mismatch)")
                    else:
                        # New section
                        resume_data['sections'][template_section] = content
                        print(f"   ✓ {template_section}: {content_preview}...")
                
                print(f"\n✅ Enhanced {len(mapped_sections)} sections with intelligent mapping")
                print(f"📋 Final resume sections: {list(resume_data.get('sections', {}).keys())}")
            else:
                print(f"\n⚠️  No sections were mapped")
        else:
            print(f"⚠️  No sections found to classify")
        
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"⚠️  Error in intelligent mapping: {e}")
        import traceback
        traceback.print_exc()
    
    return resume_data


def format_resume_with_enhanced_intelligence(resume_data: Dict, template_analysis: Dict, 
                                             output_path: str, 
                                             confidence_threshold: float = 0.6) -> bool:
    """
    Format resume with enhanced intelligent section mapping
    
    Args:
        resume_data: Parsed resume data
        template_analysis: Template analysis
        output_path: Path to save formatted resume
        confidence_threshold: Minimum confidence for classification (0-1)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Enhance resume data with intelligent mapping
        enhanced_resume_data = enhance_resume_data_with_intelligent_mapping(
            resume_data, 
            template_analysis, 
            confidence_threshold
        )
        
        # Use existing word formatter with enhanced data
        if WORD_FORMATTER_AVAILABLE:
            return format_word_document(enhanced_resume_data, template_analysis, output_path)
        else:
            print("❌ Word formatter not available")
            return False
            
    except Exception as e:
        print(f"❌ Error in enhanced formatting: {e}")
        import traceback
        traceback.print_exc()
        return False


# Backward compatibility wrapper
def format_resume_intelligent(resume_data: Dict, template_analysis: Dict, 
                              output_path: str) -> bool:
    """
    Backward compatible wrapper for existing code
    Automatically uses enhanced intelligence if available
    
    Args:
        resume_data: Parsed resume data
        template_analysis: Template analysis
        output_path: Path to save formatted resume
        
    Returns:
        True if successful, False otherwise
    """
    print(f"\n{'='*70}")
    print(f"📋 FORMAT_RESUME_INTELLIGENT CALLED")
    print(f"{'='*70}")
    print(f"   ENHANCED_CLASSIFIER_AVAILABLE: {ENHANCED_CLASSIFIER_AVAILABLE}")
    print(f"   WORD_FORMATTER_AVAILABLE: {WORD_FORMATTER_AVAILABLE}")
    print(f"   Resume sections: {list(resume_data.get('sections', {}).keys())}")
    print(f"{'='*70}\n")
    
    if ENHANCED_CLASSIFIER_AVAILABLE:
        print("🧠 Using enhanced intelligent section mapping")
        return format_resume_with_enhanced_intelligence(
            resume_data, 
            template_analysis, 
            output_path,
            confidence_threshold=0.6
        )
    else:
        print("📝 Using standard formatting (enhanced classifier not available)")
        # Try to import word_formatter dynamically (might work at runtime)
        try:
            from utils.word_formatter import format_word_document
            return format_word_document(resume_data, template_analysis, output_path)
        except ImportError as e:
            print(f"❌ Word formatter not available: {e}")
            return False
