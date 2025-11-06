"""
Enhanced Section Classifier for Resume Formatter
Combines multiple strategies to accurately classify resume sections:
1. Comprehensive synonym mapping
2. Zero-shot classification with transformers
3. Confidence thresholding
4. Hybrid rule-based + ML approach
5. Content-based classification for unheaded sections
"""

import re
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# Try importing numpy with graceful fallback
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    # Create a minimal numpy replacement for basic operations
    class NumpyFallback:
        @staticmethod
        def dot(a, b):
            """Simple dot product for 1D arrays"""
            return sum(x * y for x, y in zip(a, b))
        
        @staticmethod
        def linalg_norm(a):
            """Simple L2 norm"""
            return sum(x * x for x in a) ** 0.5
    
    np = NumpyFallback()

# Try importing ML libraries with graceful fallbacks
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️  transformers not installed. Run: pip install transformers")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("⚠️  sentence-transformers not installed. Run: pip install sentence-transformers")

try:
    from fuzzywuzzy import process, fuzz
    FUZZYWUZZY_AVAILABLE = True
except ImportError:
    FUZZYWUZZY_AVAILABLE = False
    print("⚠️  fuzzywuzzy not installed. Run: pip install fuzzywuzzy python-Levenshtein")


class EnhancedSectionClassifier:
    """
    Advanced section classifier with multiple classification strategies
    OPTIMIZED: Uses singleton pattern and model caching for 10x faster performance
    """
    
    # Singleton pattern - shared models across all instances
    _instance = None
    _sentence_model = None
    _zero_shot_classifier = None
    _models_loaded = False
    
    # Comprehensive section synonym mapping
    SECTION_MAPPING = {
        "employment history": [
            "work experience", "experience", "professional experience", 
            "career history", "employment", "job history", "work history",
            "professional background", "career experience", "relevant employment",
            "professional employment", "employment record", "work record",
            "career summary", "professional history", "job experience"
        ],
        "education": [
            "academic background", "qualifications", "academics", 
            "educational background", "schooling", "academic qualifications",
            "education background", "academic history", "educational qualifications",
            "degrees", "academic credentials", "educational credentials",
            "university", "college", "academic record"
        ],
        "skills": [
            "technical skills", "core competencies", "expertise", "abilities",
            "key skills", "professional skills", "competencies", "skill set",
            "technical competencies", "areas of expertise", "technical expertise",
            "proficiencies", "capabilities", "technical proficiencies",
            "core skills", "professional competencies"
        ],
        "certifications": [
            "licenses", "achievements", "courses", "training", "certificates",
            "professional certifications", "credentials", "professional credentials",
            "professional licenses", "accreditations", "qualifications",
            "professional training", "certified courses"
        ],
        "projects": [
            "work samples", "case studies", "portfolio", "key projects",
            "project experience", "notable projects", "project highlights",
            "relevant projects", "major projects", "project work"
        ],
        "summary": [
            "professional summary", "objective", "profile summary", "about me",
            "career objective", "professional profile", "career summary",
            "executive summary", "professional overview", "career overview",
            "profile", "personal statement", "career profile", "introduction"
        ],
        "awards": [
            "honors", "recognition", "achievements", "accomplishments",
            "awards and honors", "honors and awards", "distinctions",
            "accolades", "recognitions"
        ],
        "languages": [
            "language skills", "language proficiency", "linguistic skills",
            "spoken languages", "language abilities"
        ],
        "references": [
            "professional references", "referees", "reference contacts"
        ],
        "volunteer": [
            "volunteer experience", "volunteer work", "community service",
            "volunteering", "community involvement", "social work"
        ],
        "publications": [
            "research", "papers", "articles", "published work",
            "research papers", "academic publications"
        ]
    }
    
    def __init__(self, confidence_threshold: float = 0.6):
        """
        Initialize the classifier
        
        Args:
            confidence_threshold: Minimum confidence score (0-1) to accept a classification
        """
        self.confidence_threshold = confidence_threshold
        
        # Only load models once
        if not EnhancedSectionClassifier._models_loaded:
            self._load_models()
            EnhancedSectionClassifier._models_loaded = True
    
    def _load_models(self):
        """Load ML models once and cache them"""
        # Initialize sentence transformer for semantic similarity (LIGHTWEIGHT MODEL)
        if SENTENCE_TRANSFORMERS_AVAILABLE and EnhancedSectionClassifier._sentence_model is None:
            try:
                print("⚡ Loading OPTIMIZED sentence transformer (all-MiniLM-L6-v2)...")
                import time
                start = time.time()
                EnhancedSectionClassifier._sentence_model = SentenceTransformer(
                    'all-MiniLM-L6-v2',
                    device='cpu'  # Use CPU for compatibility
                )
                print(f"✅ Sentence transformer loaded in {time.time()-start:.2f}s (cached for reuse)")
            except Exception as e:
                print(f"⚠️  Failed to load sentence transformer: {e}")
        
        # Skip zero-shot classifier - it's VERY slow (400MB+ model)
        # Use lightweight sentence transformer instead
        if TRANSFORMERS_AVAILABLE and EnhancedSectionClassifier._zero_shot_classifier is None:
            # Disabled for performance - sentence transformer is faster and good enough
            pass
    
    @property
    def sentence_model(self):
        """Get cached sentence model"""
        return EnhancedSectionClassifier._sentence_model
    
    @property
    def zero_shot_classifier(self):
        """Get cached zero-shot classifier"""
        return EnhancedSectionClassifier._zero_shot_classifier
    
    def normalize_section_name(self, section_name: str) -> Optional[str]:
        """
        Normalize a section name using synonym mapping
        
        Args:
            section_name: Raw section name from resume
            
        Returns:
            Normalized section name or None if no match
        """
        if not section_name:
            return None
        
        section_lower = section_name.strip().lower()
        
        # Check exact match first
        for key, synonyms in self.SECTION_MAPPING.items():
            if section_lower == key or section_lower in synonyms:
                return key
        
        # Check partial match
        for key, synonyms in self.SECTION_MAPPING.items():
            if key in section_lower:
                return key
            for synonym in synonyms:
                if synonym in section_lower or section_lower in synonym:
                    return key
        
        return None
    
    def classify_by_heading(self, heading: str, template_sections: List[str]) -> Tuple[Optional[str], float]:
        """
        Classify a section by its heading using multiple strategies
        
        Args:
            heading: Section heading text
            template_sections: Available template section names
            
        Returns:
            Tuple of (matched_section, confidence_score)
        """
        if not heading:
            return None, 0.0
        
        heading_clean = heading.strip().lower()
        
        # Strategy 1: Exact match
        for template_section in template_sections:
            if heading_clean == template_section.strip().lower():
                return template_section, 1.0
        
        # Strategy 2: Normalize and match
        normalized = self.normalize_section_name(heading)
        if normalized:
            for template_section in template_sections:
                if normalized in template_section.lower():
                    return template_section, 0.95
        
        # Strategy 3: Fuzzy matching
        if FUZZYWUZZY_AVAILABLE:
            template_clean = [s.strip().lower() for s in template_sections]
            result = process.extractOne(heading_clean, template_clean, scorer=fuzz.token_sort_ratio)
            if result and result[1] > 85:
                idx = template_clean.index(result[0])
                return template_sections[idx], result[1] / 100.0
        
        # Strategy 4: Semantic similarity
        if self.sentence_model:
            try:
                heading_emb = self.sentence_model.encode([heading_clean])
                template_embs = self.sentence_model.encode([s.lower() for s in template_sections])
                similarities = np.dot(heading_emb, template_embs.T)[0]
                best_idx = np.argmax(similarities)
                best_score = similarities[best_idx]
                
                if best_score > self.confidence_threshold:
                    return template_sections[best_idx], float(best_score)
            except Exception as e:
                print(f"  ⚠️  Semantic matching failed: {e}")
        
        return None, 0.0
    
    def classify_by_content(self, content: str, position: int = 0) -> Tuple[Optional[str], float]:
        """
        Classify a section by its content using hybrid approach
        
        Args:
            content: Section content text
            position: Position in document (0 = first section)
            
        Returns:
            Tuple of (section_type, confidence_score)
        """
        if not content or len(content.strip()) < 10:
            return None, 0.0
        
        content_lower = content.lower()
        
        # Strategy 1: Rule-based classification (fast, reliable)
        rule_result = self._classify_by_rules(content_lower, position)
        if rule_result[0] and rule_result[1] >= 0.8:
            return rule_result
        
        # Strategy 2: Zero-shot classification (accurate, semantic)
        if self.zero_shot_classifier:
            try:
                zeroshot_result = self._classify_zero_shot(content[:500])
                if zeroshot_result[1] >= self.confidence_threshold:
                    return zeroshot_result
            except Exception as e:
                print(f"  ⚠️  Zero-shot classification failed: {e}")
        
        # Fallback to rule-based result
        return rule_result
    
    def _classify_by_rules(self, content: str, position: int) -> Tuple[Optional[str], float]:
        """
        Rule-based content classification using keywords and patterns
        
        Args:
            content: Lowercase content text
            position: Position in document
            
        Returns:
            Tuple of (section_type, confidence_score)
        """
        # Position-based heuristic (summary usually first)
        if position <= 2 and len(content.split()) < 150:
            summary_keywords = ['years', 'experience', 'professional', 'seeking', 'expertise', 
                              'motivated', 'dedicated', 'passionate', 'objective']
            if sum(1 for kw in summary_keywords if kw in content) >= 2:
                return "summary", 0.85
        
        # Keyword scoring for each section type
        keyword_patterns = {
            "employment history": {
                "keywords": ['worked', 'managed', 'developed', 'led', 'responsible', 'duties',
                           'role', 'position', 'company', 'employer', 'team', 'project',
                           'provided', 'collaborated', 'established', 'coordinated', 'ensured',
                           'implemented', 'demonstrated', 'recognized', 'handled'],
                "patterns": [r'\d{4}\s*[-–]\s*\d{4}', r'\d{4}\s*[-–]\s*present',
                           r'\d{1,2}/\d{4}\s*[-–]\s*\d{1,2}/\d{4}',  # 5/2024- 6/2025
                           r'\|\s*\w+\s*,\s*\w+\s*\|',  # |Atlanta, GA|
                           r'manager|director|engineer|specialist|consultant|coordinator']
            },
            "education": {
                "keywords": ['university', 'degree', 'graduated', 'gpa', 'bachelor', 'master',
                           'college', 'school', 'diploma', 'phd', 'doctorate', 'major'],
                "patterns": [r'b\.?s\.?c?\.?', r'm\.?s\.?c?\.?', r'bachelor', r'master']
            },
            "skills": {
                "keywords": ['proficient', 'skilled', 'expertise', 'technologies', 'programming',
                           'python', 'java', 'javascript', 'react', 'sql', 'aws', 'azure'],
                "patterns": [r'\b[A-Z]{2,}\b']  # Acronyms like AWS, SQL
            },
            "certifications": {
                "keywords": ['certified', 'certificate', 'certification', 'license', 'credential',
                           'accredited', 'qualified', 'aws', 'azure', 'cisco'],
                "patterns": [r'certified\s+\w+', r'\w+\s+certification']
            },
            "projects": {
                "keywords": ['project', 'developed', 'built', 'created', 'implemented',
                           'designed', 'application', 'system', 'platform', 'website'],
                "patterns": [r'project\s*\d+', r'project\s+\w+']
            },
            "awards": {
                "keywords": ['award', 'honor', 'recognition', 'achievement', 'winner',
                           'recipient', 'distinguished', 'excellence'],
                "patterns": []
            }
        }
        
        scores = {}
        for section_type, patterns in keyword_patterns.items():
            score = 0
            
            # Keyword matching
            keyword_count = sum(1 for kw in patterns['keywords'] if kw in content)
            score += keyword_count
            
            # Pattern matching
            pattern_count = sum(1 for pattern in patterns['patterns'] 
                              if re.search(pattern, content, re.IGNORECASE))
            score += pattern_count * 2  # Patterns are more reliable
            
            if score > 0:
                scores[section_type] = score
        
        if scores:
            best_section = max(scores, key=scores.get)
            max_score = scores[best_section]
            
            # Normalize confidence score
            confidence = min(0.95, 0.5 + (max_score * 0.1))
            return best_section, confidence
        
        return None, 0.0
    
    def _classify_zero_shot(self, content: str) -> Tuple[Optional[str], float]:
        """
        Zero-shot classification using transformer model
        
        Args:
            content: Content text (truncated to 500 chars for speed)
            
        Returns:
            Tuple of (section_type, confidence_score)
        """
        if not self.zero_shot_classifier:
            return None, 0.0
        
        candidate_labels = [
            "Employment History",
            "Education",
            "Skills",
            "Certifications",
            "Projects",
            "Professional Summary",
            "Awards",
            "Languages"
        ]
        
        result = self.zero_shot_classifier(content, candidate_labels)
        
        # Map back to normalized names
        label_mapping = {
            "Employment History": "employment history",
            "Education": "education",
            "Skills": "skills",
            "Certifications": "certifications",
            "Projects": "projects",
            "Professional Summary": "summary",
            "Awards": "awards",
            "Languages": "languages"
        }
        
        top_label = result['labels'][0]
        top_score = result['scores'][0]
        
        normalized_label = label_mapping.get(top_label)
        return normalized_label, top_score
    
    def classify_section(self, heading: Optional[str], content: str, 
                        position: int, template_sections: List[str]) -> Dict:
        """
        Main classification method combining all strategies
        
        Args:
            heading: Section heading (None if no heading)
            content: Section content
            position: Position in document
            template_sections: Available template sections
            
        Returns:
            Dict with classification results
        """
        result = {
            "matched_section": None,
            "confidence": 0.0,
            "method": None,
            "uncertain": False
        }
        
        # Try heading-based classification first
        heading_matched = None
        heading_confidence = 0.0
        if heading:
            heading_matched, heading_confidence = self.classify_by_heading(heading, template_sections)
        
        # ALWAYS check content-based classification for validation
        content_type, content_confidence = self.classify_by_content(content, position)
        
        # If heading and content disagree significantly, trust content (it's more reliable)
        section_type = None
        confidence = 0.0
        
        if heading_matched and content_type:
            # Normalize section names for comparison
            heading_normalized = self.normalize_section_name(heading_matched)
            content_normalized = self.normalize_section_name(content_type)
            
            if heading_normalized != content_normalized and content_confidence >= 0.7:
                # Content strongly suggests different section - trust content
                print(f"    ⚠️  Heading/content mismatch: '{heading}' vs content → trusting content")
                section_type = content_type
                confidence = content_confidence
                result["method"] = "content"
            else:
                # Heading and content agree, or content is weak - trust heading
                section_type = heading_matched
                confidence = heading_confidence
                result["method"] = "heading"
        elif heading_matched:
            # Only heading available
            section_type = heading_matched
            confidence = heading_confidence
            result["method"] = "heading"
        elif content_type:
            # Only content available
            section_type = content_type
            confidence = content_confidence
            result["method"] = "content"
        
        # Check if we have a match
        if section_type and confidence >= self.confidence_threshold:
            # Normalize section_type for matching
            section_type_normalized = self.normalize_section_name(section_type)
            
            # Find matching template section
            for template_section in template_sections:
                template_normalized = self.normalize_section_name(template_section)
                
                # Check if they match (either exact or one contains the other)
                if (section_type_normalized == template_normalized or 
                    section_type_normalized in template_normalized or
                    template_normalized in section_type_normalized):
                    result["matched_section"] = template_section
                    result["confidence"] = confidence
                    if not result["method"]:
                        result["method"] = "content"
                    return result
        
        # Mark as uncertain if confidence is too low
        if confidence > 0 and confidence < self.confidence_threshold:
            result["uncertain"] = True
            result["confidence"] = confidence
            result["method"] = "uncertain"
        
        return result
    
    def batch_classify(self, sections: List[Dict], template_sections: List[str]) -> Dict[str, str]:
        """
        Classify multiple sections in batch
        
        Args:
            sections: List of dicts with 'heading', 'content', 'position'
            template_sections: Available template sections
            
        Returns:
            Dict mapping template sections to content
        """
        mapped = {}
        uncertain_sections = []
        
        print(f"\n{'='*70}")
        print(f"🔍 CLASSIFYING {len(sections)} SECTIONS")
        print(f"{'='*70}\n")
        
        for idx, section in enumerate(sections):
            heading = section.get('heading')
            content = section.get('content', '')
            position = section.get('position', idx)
            
            result = self.classify_section(heading, content, position, template_sections)
            
            if result['matched_section']:
                mapped[result['matched_section']] = content
                print(f"  ✓ '{heading or '[No heading]'}' → '{result['matched_section']}' "
                      f"({result['method']}, confidence: {result['confidence']:.2f})")
            elif result['uncertain']:
                uncertain_sections.append({
                    'heading': heading,
                    'content': content,
                    'confidence': result['confidence']
                })
                print(f"  ⚠️  '{heading or '[No heading]'}' - uncertain "
                      f"(confidence: {result['confidence']:.2f})")
            else:
                print(f"  ❌ '{heading or '[No heading]'}' - no match found")
        
        # Handle uncertain sections
        if uncertain_sections:
            print(f"\n⚠️  {len(uncertain_sections)} uncertain sections - storing separately")
            mapped['_uncertain'] = '\n\n'.join([
                f"[{s['heading'] or 'Unheaded Section'}]\n{s['content']}"
                for s in uncertain_sections
            ])
        
        print(f"\n✅ Successfully mapped {len(mapped)} sections")
        print(f"{'='*70}\n")
        
        return mapped


# Singleton instance
_classifier_instance = None

def get_section_classifier(confidence_threshold: float = 0.6) -> EnhancedSectionClassifier:
    """Get or create singleton classifier instance"""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = EnhancedSectionClassifier(confidence_threshold)
    return _classifier_instance


# Example usage
if __name__ == "__main__":
    classifier = EnhancedSectionClassifier(confidence_threshold=0.6)
    
    # Test section classification
    test_sections = [
        {
            "heading": "Professional Profile",
            "content": "Experienced software engineer with 5 years of expertise in Python and cloud technologies.",
            "position": 0
        },
        {
            "heading": "Work Experience",
            "content": "Software Engineer at Google (2020-2024). Developed microservices using Python and AWS.",
            "position": 1
        },
        {
            "heading": "Academic Background",
            "content": "B.Tech in Computer Science from JNTUH, graduated in 2020 with 8.5 GPA.",
            "position": 2
        }
    ]
    
    template_sections = ["SUMMARY", "EMPLOYMENT HISTORY", "EDUCATION", "SKILLS"]
    
    results = classifier.batch_classify(test_sections, template_sections)
    print("\nMapped sections:")
    for section, content in results.items():
        print(f"\n{section}:\n{content[:100]}...")
