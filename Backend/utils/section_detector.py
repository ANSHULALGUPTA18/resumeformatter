"""
Multi-Layer Section Detector
Combines rule-based and ML-based approaches for accurate section detection
"""
import re
from typing import Dict, List, Tuple

class SectionDetector:
    """
    Multi-layer section detection system
    Layer 1: Rule-based boundary detection (structural)
    Layer 2: Keyword-based classification (heuristic)
    Layer 3: ML refinement (semantic) - optional
    """
    
    # Section header patterns (case-insensitive)
    SECTION_HEADERS = {
        'employment': [
            'employment history', 'work experience', 'professional experience',
            'work history', 'career history', 'professional background',
            'experience', 'employment', 'work background', 'career summary',
            'professional summary', 'job history'
        ],
        'education': [
            'education', 'academic background', 'educational background',
            'academic qualifications', 'qualifications', 'academics',
            'education background', 'academic credentials'
        ],
        'skills': [
            'skills', 'technical skills', 'core competencies',
            'competencies', 'expertise', 'abilities', 'proficiencies',
            'technical expertise', 'key skills'
        ],
        'certifications': [
            'certifications', 'certificates', 'licenses', 'credentials',
            'professional certifications', 'training', 'courses',
            'professional development', 'licenses and certifications'
        ],
        'summary': [
            'summary', 'professional summary', 'profile', 'objective',
            'career objective', 'executive summary', 'overview',
            'professional profile', 'about me'
        ],
        'projects': [
            'projects', 'portfolio', 'key projects', 'notable projects',
            'project experience', 'project highlights'
        ],
        'awards': [
            'awards', 'honors', 'achievements', 'recognition',
            'awards and honors', 'accomplishments'
        ],
        'publications': [
            'publications', 'research', 'papers', 'articles',
            'published works', 'research papers'
        ],
        'languages': [
            'languages', 'language proficiency', 'language skills'
        ],
        'references': [
            'references', 'professional references', 'references available'
        ]
    }
    
    # Content keywords for validation
    CONTENT_KEYWORDS = {
        'employment': [
            'managed', 'developed', 'implemented', 'led', 'created',
            'designed', 'built', 'worked', 'responsible', 'achieved',
            'improved', 'increased', 'reduced', 'coordinated', 'supervised',
            'maintained', 'executed', 'delivered', 'collaborated', 'established'
        ],
        'education': [
            'university', 'college', 'degree', 'bachelor', 'master',
            'phd', 'doctorate', 'graduated', 'gpa', 'major', 'minor',
            'coursework', 'thesis', 'dissertation', 'studied'
        ],
        'skills': [
            'python', 'java', 'javascript', 'sql', 'aws', 'azure',
            'docker', 'kubernetes', 'react', 'angular', 'node',
            'proficient', 'experienced', 'familiar', 'expert'
        ],
        'certifications': [
            'certified', 'certification', 'license', 'credential',
            'completed', 'issued', 'valid', 'expires', 'accredited',
            'certificate', 'course completion'
        ]
    }
    
    def __init__(self, use_ml=False):
        self.use_ml = use_ml
        # Use singleton cached model for performance
        self.ml_model = None
        if use_ml:
            try:
                from sentence_transformers import SentenceTransformer
                # Check if model is already cached
                if not hasattr(SectionDetector, '_cached_model'):
                    print("  ⚡ Loading OPTIMIZED ML section detector (all-MiniLM-L6-v2)...")
                    import time
                    start = time.time()
                    SectionDetector._cached_model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
                    print(f"  ✅ ML section detector loaded in {time.time()-start:.2f}s (cached)")
                self.ml_model = SectionDetector._cached_model
            except Exception as e:
                print(f"  ⚠️  ML model not available: {e}, using rule-based only")
                self.use_ml = False
    
    def segment_resume(self, text: str) -> Dict[str, str]:
        """
        Layer 1: Rule-based boundary detection
        Split resume into sections based on headers
        """
        segments = {}
        current_section = None
        current_lines = []
        
        lines = text.split('\n')
        
        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue
            
            # Check if this line is a section header
            detected_section = self._detect_section_header(line_clean)
            
            if detected_section:
                # Save previous section
                if current_section and current_lines:
                    segments[current_section] = '\n'.join(current_lines).strip()
                
                # Start new section
                current_section = detected_section
                current_lines = []
            else:
                # Add line to current section
                if current_section:
                    current_lines.append(line)
        
        # Save last section
        if current_section and current_lines:
            segments[current_section] = '\n'.join(current_lines).strip()
        
        return segments
    
    def _detect_section_header(self, line: str) -> str:
        """
        Detect if a line is a section header
        Returns section name or None
        """
        line_lower = line.lower().strip()
        
        # Must be short (headers are typically < 50 chars)
        if len(line) > 50:
            return None
        
        # Check against known headers
        for section, patterns in self.SECTION_HEADERS.items():
            for pattern in patterns:
                if pattern in line_lower:
                    # Additional validation: check if it's likely a header
                    # Headers usually don't have periods or commas
                    if '.' not in line and ',' not in line:
                        return section
        
        return None
    
    def validate_section_content(self, section: str, content: str, confidence_threshold=0.6) -> Tuple[bool, float]:
        """
        Layer 2: Validate section content using keyword heuristics
        Returns (is_valid, confidence_score)
        """
        if not content or len(content) < 10:
            return False, 0.0
        
        content_lower = content.lower()
        
        # Get expected keywords for this section
        expected_keywords = self.CONTENT_KEYWORDS.get(section, [])
        if not expected_keywords:
            return True, 1.0  # No validation rules, assume valid
        
        # Count keyword matches
        matches = sum(1 for kw in expected_keywords if kw in content_lower)
        confidence = matches / len(expected_keywords) if expected_keywords else 0.0
        
        is_valid = confidence >= confidence_threshold
        
        return is_valid, confidence
    
    def guess_section_by_keywords(self, text: str) -> str:
        """
        Layer 2: Guess section type based on content keywords
        Used when section header is ambiguous or missing
        """
        text_lower = text.lower()
        
        # Score each section type
        scores = {}
        for section, keywords in self.CONTENT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            scores[section] = score
        
        # Return section with highest score
        if scores:
            best_section = max(scores, key=scores.get)
            if scores[best_section] > 0:
                return best_section
        
        return 'unknown'
    
    def refine_with_ml(self, text: str, candidate_sections: List[str]) -> str:
        """
        Layer 3: ML-based refinement for ambiguous cases
        Uses sentence transformers to classify section
        """
        if not self.use_ml or not self.ml_model:
            return candidate_sections[0] if candidate_sections else 'unknown'
        
        try:
            # Create embeddings for text and section names
            text_embedding = self.ml_model.encode(text)
            section_embeddings = self.ml_model.encode(candidate_sections)
            
            # Calculate similarity scores
            from sklearn.metrics.pairwise import cosine_similarity
            similarities = cosine_similarity([text_embedding], section_embeddings)[0]
            
            # Return section with highest similarity
            best_idx = similarities.argmax()
            confidence = similarities[best_idx]
            
            if confidence > 0.5:
                return candidate_sections[best_idx]
        except Exception as e:
            print(f"  ⚠️  ML refinement error: {e}")
        
        return candidate_sections[0] if candidate_sections else 'unknown'
    
    def detect_and_validate(self, text: str) -> Dict[str, Dict]:
        """
        Complete multi-layer detection and validation
        Returns sections with confidence scores
        """
        # Layer 1: Segment by headers
        segments = self.segment_resume(text)
        
        # Layer 2: Validate each section
        validated_segments = {}
        for section, content in segments.items():
            is_valid, confidence = self.validate_section_content(section, content)
            
            if not is_valid and confidence < 0.3:
                # Content doesn't match section - try to reclassify
                guessed_section = self.guess_section_by_keywords(content)
                print(f"  ⚠️  Section '{section}' content mismatch (confidence: {confidence:.2f})")
                print(f"     → Reclassified as '{guessed_section}'")
                section = guessed_section
            
            validated_segments[section] = {
                'content': content,
                'confidence': confidence,
                'validated': is_valid
            }
        
        return validated_segments
    
    def detect_section_boundaries(self, paragraphs: List) -> Dict[str, List[int]]:
        """
        Detect section boundaries in a list of paragraphs
        Returns dict mapping section names to paragraph indices
        """
        boundaries = {}
        current_section = None
        current_indices = []
        
        for idx, para in enumerate(paragraphs):
            text = para.text.strip() if hasattr(para, 'text') else str(para).strip()
            
            # Check if this is a section header
            detected_section = self._detect_section_header(text)
            
            if detected_section:
                # Save previous section
                if current_section and current_indices:
                    boundaries[current_section] = current_indices
                
                # Start new section
                current_section = detected_section
                current_indices = [idx]
            else:
                # Add to current section
                if current_section:
                    current_indices.append(idx)
        
        # Save last section
        if current_section and current_indices:
            boundaries[current_section] = current_indices
        
        return boundaries
    
    def is_employment_content(self, text: str) -> bool:
        """Quick check if text looks like employment content"""
        text_lower = text.lower()
        employment_verbs = ['managed', 'developed', 'led', 'created', 'implemented', 'designed', 'built']
        return any(verb in text_lower for verb in employment_verbs)
    
    def is_certification_content(self, text: str) -> bool:
        """Quick check if text looks like certification content"""
        text_lower = text.lower()
        cert_keywords = ['certified', 'certification', 'license', 'completed', 'issued']
        return any(kw in text_lower for kw in cert_keywords)
    
    def is_skills_content(self, text: str) -> bool:
        """Quick check if text looks like skills content"""
        # Skills are usually comma-separated or short bullet points
        if ',' in text and len(text) < 200:
            return True
        # Check for common skill keywords
        text_lower = text.lower()
        skill_keywords = ['python', 'java', 'sql', 'aws', 'proficient', 'experienced']
        return any(kw in text_lower for kw in skill_keywords)

# Global instance
section_detector = SectionDetector(use_ml=True)
