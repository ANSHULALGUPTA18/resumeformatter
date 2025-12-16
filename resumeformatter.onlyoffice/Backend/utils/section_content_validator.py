"""
Section Content Validator - Prevents content mixing between sections
Ensures employment points stay in employment, certifications in certifications, etc.
"""

import re
from typing import Dict, List, Tuple, Optional


class SectionContentValidator:
    """
    Validates that section content matches the section type
    Prevents employment history points from appearing in certifications, etc.
    """
    
    # Strong indicators for each section type
    SECTION_INDICATORS = {
        'EMPLOYMENT': {
            'strong_keywords': [
                'worked', 'managed', 'developed', 'led', 'responsible for',
                'duties included', 'role', 'position', 'company', 'employer',
                'team', 'collaborated', 'coordinated', 'supervised', 'implemented'
            ],
            'patterns': [
                r'\d{4}\s*[-–]\s*\d{4}',  # Date ranges: 2020-2023
                r'\d{4}\s*[-–]\s*present',  # 2020-present
                r'\d{1,2}/\d{4}\s*[-–]\s*\d{1,2}/\d{4}',  # 5/2024-6/2025
                r'(manager|director|engineer|specialist|consultant|coordinator|analyst)',
                r'(company|corporation|inc\.|llc|ltd)',
            ],
            'anti_keywords': ['certified', 'certificate', 'license', 'python', 'java', 'aws']
        },
        'EDUCATION': {
            'strong_keywords': [
                'university', 'college', 'school', 'degree', 'bachelor', 'master',
                'phd', 'doctorate', 'graduated', 'gpa', 'major', 'minor', 'diploma'
            ],
            'patterns': [
                r'b\.?s\.?c?\.?|bachelor',
                r'm\.?s\.?c?\.?|master',
                r'phd|doctorate',
                r'gpa:?\s*\d\.\d',
            ],
            'anti_keywords': ['worked', 'managed', 'developed', 'company', 'employer']
        },
        'SKILLS': {
            'strong_keywords': [
                'python', 'java', 'javascript', 'react', 'node', 'sql', 'aws', 'azure',
                'docker', 'kubernetes', 'git', 'html', 'css', 'api', 'database',
                'proficient', 'skilled', 'expertise', 'technologies', 'tools'
            ],
            'patterns': [
                r'\b[A-Z]{2,}\b',  # Acronyms: AWS, SQL, API
                r'(python|java|javascript|react|angular|vue|node)',
            ],
            'anti_keywords': ['worked at', 'company', 'employer', 'managed team']
        },
        'CERTIFICATIONS': {
            'strong_keywords': [
                'certified', 'certificate', 'certification', 'license', 'licensed',
                'credential', 'accredited', 'qualified', 'exam', 'test', 'passed',
                'aws certified', 'microsoft certified', 'cisco certified', 'comptia'
            ],
            'patterns': [
                r'certified\s+\w+',
                r'\w+\s+certified',
                r'license\s+#?\d+',
                r'certification\s+in\s+\w+',
            ],
            'anti_keywords': [
                'worked', 'managed', 'developed', 'team', 'project', 'experience',
                'professional', 'years of experience', 'expertise in', 'skilled in',
                'background in', 'proficient in', 'adept at', 'hands-on experience'
            ]
        },
        'PROJECTS': {
            'strong_keywords': [
                'project', 'developed', 'built', 'created', 'implemented', 'designed',
                'application', 'system', 'platform', 'website', 'app', 'tool'
            ],
            'patterns': [
                r'project\s*\d+',
                r'project\s+\w+',
                r'(built|created|developed)\s+(a|an|the)\s+\w+',
            ],
            'anti_keywords': ['certified', 'certificate', 'license']
        },
        'SUMMARY': {
            'strong_keywords': [
                'years of experience', 'professional', 'seeking', 'motivated',
                'dedicated', 'passionate', 'expertise in', 'specialized in',
                'experienced', 'skilled in', 'background in', 'proficient in',
                'adept at', 'hands-on experience', 'professional profile'
            ],
            'patterns': [
                r'\d+\+?\s*years?\s+of\s+experience',
                r'seeking\s+(a|an)\s+\w+\s+position',
                r'experienced\s+\w+\s+(engineer|analyst|developer|manager)',
                r'professional\s+profile',
            ],
            'anti_keywords': ['certified', 'certificate', 'license', 'worked at specific company']
        }
    }
    
    def __init__(self, confidence_threshold: float = 0.6):
        """
        Initialize validator
        
        Args:
            confidence_threshold: Minimum confidence to accept content (0-1)
        """
        self.confidence_threshold = confidence_threshold
    
    def validate_content(self, content: str, section_type: str) -> Tuple[bool, float, str]:
        """
        Validate if content belongs to the specified section type
        
        Args:
            content: The content text to validate
            section_type: The section type (EMPLOYMENT, EDUCATION, etc.)
            
        Returns:
            Tuple of (is_valid, confidence_score, reason)
        """
        if not content or not section_type:
            return False, 0.0, "Empty content or section type"
        
        content_lower = content.lower()
        section_upper = section_type.upper()
        
        # Get indicators for this section type
        indicators = self.SECTION_INDICATORS.get(section_upper, {})
        if not indicators:
            # Unknown section type - accept by default
            return True, 1.0, "Unknown section type - accepted"
        
        strong_keywords = indicators.get('strong_keywords', [])
        patterns = indicators.get('patterns', [])
        anti_keywords = indicators.get('anti_keywords', [])
        
        # Calculate scores
        keyword_score = 0
        pattern_score = 0
        anti_score = 0
        
        # Check strong keywords
        for keyword in strong_keywords:
            if keyword in content_lower:
                keyword_score += 1
        
        # Check patterns
        for pattern in patterns:
            if re.search(pattern, content_lower, re.IGNORECASE):
                pattern_score += 1
        
        # Check anti-keywords (indicators of WRONG section)
        for anti_kw in anti_keywords:
            if anti_kw in content_lower:
                anti_score += 1
        
        # Calculate confidence
        positive_score = keyword_score + (pattern_score * 2)  # Patterns are stronger
        negative_score = anti_score * 3  # Anti-keywords are strong negative signals
        
        total_score = positive_score - negative_score
        max_possible = len(strong_keywords) + (len(patterns) * 2)
        
        if max_possible > 0:
            confidence = max(0.0, min(1.0, total_score / max_possible))
        else:
            confidence = 0.5  # Neutral if no indicators
        
        # Determine validity
        is_valid = confidence >= self.confidence_threshold
        
        # Generate reason
        if is_valid:
            reason = f"Content matches {section_upper} (score: {total_score}, confidence: {confidence:.2f})"
        else:
            if anti_score > 0:
                reason = f"Content has {anti_score} anti-keywords suggesting wrong section"
            else:
                reason = f"Content doesn't match {section_upper} indicators (confidence: {confidence:.2f})"
        
        return is_valid, confidence, reason
    
    def classify_content_type(self, content: str) -> Tuple[Optional[str], float]:
        """
        Classify what type of section this content belongs to
        
        Args:
            content: The content text to classify
            
        Returns:
            Tuple of (section_type, confidence_score)
        """
        if not content:
            return None, 0.0
        
        scores = {}
        
        # Test against all section types
        for section_type in self.SECTION_INDICATORS.keys():
            is_valid, confidence, _ = self.validate_content(content, section_type)
            if is_valid:
                scores[section_type] = confidence
        
        if scores:
            best_section = max(scores, key=scores.get)
            best_confidence = scores[best_section]
            return best_section, best_confidence
        
        return None, 0.0
    
    def filter_mismatched_content(self, content: str, section_type: str) -> Tuple[str, List[str]]:
        """
        Filter out content that doesn't belong to the section
        
        Args:
            content: The content text
            section_type: The intended section type
            
        Returns:
            Tuple of (filtered_content, removed_lines)
        """
        if not content:
            return content, []
        
        lines = content.split('\n')
        filtered_lines = []
        removed_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                filtered_lines.append(line)
                continue
            
            # Validate each line
            is_valid, confidence, reason = self.validate_content(line, section_type)
            
            if is_valid:
                filtered_lines.append(line)
            else:
                removed_lines.append(f"{line} (Reason: {reason})")
                print(f"  ⚠️  Filtered out: {line[:50]}... from {section_type}")
        
        filtered_content = '\n'.join(filtered_lines)
        return filtered_content, removed_lines
    
    def suggest_correct_section(self, content: str, current_section: str) -> Optional[str]:
        """
        Suggest the correct section for misplaced content
        
        Args:
            content: The content text
            current_section: The current (incorrect) section
            
        Returns:
            Suggested section type, or None if current is correct
        """
        # Validate current section
        is_valid, confidence, _ = self.validate_content(content, current_section)
        
        if is_valid and confidence > 0.7:
            # Current section is fine
            return None
        
        # Find better section
        best_section, best_confidence = self.classify_content_type(content)
        
        if best_section and best_section != current_section.upper() and best_confidence > confidence + 0.2:
            return best_section
        
        return None


# Singleton instance
_validator_instance = None

def get_content_validator() -> SectionContentValidator:
    """Get or create the singleton content validator"""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = SectionContentValidator()
    return _validator_instance
