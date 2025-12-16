"""
Smart Section Mapper - Intelligent section name matching using ML
Uses Sentence Transformers + FuzzyWuzzy for fast and accurate section mapping
"""

import numpy as np
from typing import List, Optional, Dict, Tuple
import re

# Try to import ML libraries (graceful fallback if not installed)
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

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("⚠️  spacy not installed. Run: pip install spacy && python -m spacy download en_core_web_sm")


class SmartSectionMapper:
    """
    Intelligent section name mapper using hybrid approach:
    1. Fuzzy matching (fast, catches typos and minor variations)
    2. Semantic similarity (accurate, handles synonyms)
    3. Rule-based fallback (reliable baseline)
    """
    
    def __init__(self):
        """Initialize the mapper with ML models"""
        self.model = None
        self.nlp = None
        
        # Load sentence transformer model (lightweight, fast)
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                print("📦 Loading sentence transformer model (all-MiniLM-L6-v2)...")
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                print("✅ Sentence transformer loaded successfully")
            except Exception as e:
                print(f"⚠️  Failed to load sentence transformer: {e}")
                self.model = None
        
        # Load spaCy model for content classification
        if SPACY_AVAILABLE:
            try:
                print("📦 Loading spaCy model (en_core_web_sm)...")
                self.nlp = spacy.load("en_core_web_sm")
                print("✅ spaCy loaded successfully")
            except Exception as e:
                print(f"⚠️  Failed to load spaCy: {e}")
                try:
                    print("📥 Downloading spaCy model...")
                    import subprocess
                    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
                    self.nlp = spacy.load("en_core_web_sm")
                    print("✅ spaCy model downloaded and loaded")
                except Exception as e2:
                    print(f"⚠️  Failed to download spaCy model: {e2}")
                    self.nlp = None
        
        # Standard section name mappings (for rule-based fallback)
        self.section_synonyms = {
            'EMPLOYMENT': [
                'employment history', 'work experience', 'professional experience',
                'work history', 'career history', 'experience', 'professional background',
                'employment', 'career experience', 'relevant employment history'
            ],
            'EDUCATION': [
                'education', 'educational background', 'academic background',
                'academic qualifications', 'qualifications', 'education background',
                'certificates', 'certifications', 'credentials', 'academics',
                'education/certificates', 'education / certificates'
            ],
            'SKILLS': [
                'skills', 'technical skills', 'core competencies', 'key skills',
                'professional skills', 'areas of expertise', 'competencies',
                'technical competencies', 'skill set', 'expertise'
            ],
            'SUMMARY': [
                'summary', 'professional summary', 'career summary', 'profile',
                'professional profile', 'career objective', 'objective',
                'executive summary', 'career overview', 'professional overview'
            ],
            'PROJECTS': [
                'projects', 'key projects', 'project experience', 'notable projects',
                'project highlights', 'relevant projects'
            ],
            'CERTIFICATIONS': [
                'certifications', 'certificates', 'professional certifications',
                'licenses', 'credentials', 'professional credentials'
            ],
            'AWARDS': [
                'awards', 'honors', 'achievements', 'recognition',
                'awards and honors', 'honors and awards'
            ],
            'LANGUAGES': [
                'languages', 'language skills', 'language proficiency'
            ]
        }
    
    def map_section(self, candidate_heading: str, template_sections: List[str], 
                   confidence_threshold: float = 0.6) -> Optional[str]:
        """
        Map a candidate section heading to the best matching template section.
        
        Args:
            candidate_heading: The section heading from candidate's resume
            template_sections: List of valid section names in the template
            confidence_threshold: Minimum similarity score (0-1) to accept a match
            
        Returns:
            Best matching template section name, or None if no good match
        """
        if not candidate_heading or not template_sections:
            return None
        
        candidate_clean = candidate_heading.strip().lower()
        template_clean = [s.strip().lower() for s in template_sections]
        
        # Step 1: Exact match (fastest)
        if candidate_clean in template_clean:
            idx = template_clean.index(candidate_clean)
            return template_sections[idx]
        
        # Step 2: Fuzzy matching (fast, catches typos)
        if FUZZYWUZZY_AVAILABLE:
            fuzzy_result = process.extractOne(
                candidate_clean,
                template_clean,
                scorer=fuzz.token_sort_ratio
            )
            
            if fuzzy_result and fuzzy_result[1] > 85:  # High confidence threshold
                idx = template_clean.index(fuzzy_result[0])
                print(f"  🔍 Fuzzy match: '{candidate_heading}' → '{template_sections[idx]}' (score: {fuzzy_result[1]})")
                return template_sections[idx]
        
        # Step 3: Semantic similarity (accurate, handles synonyms)
        if self.model is not None:
            try:
                candidate_emb = self.model.encode([candidate_clean])
                template_embs = self.model.encode(template_clean)
                
                similarities = np.dot(candidate_emb, template_embs.T)[0]
                best_idx = np.argmax(similarities)
                best_score = similarities[best_idx]
                
                if best_score > confidence_threshold:
                    print(f"  🧠 Semantic match: '{candidate_heading}' → '{template_sections[best_idx]}' (score: {best_score:.2f})")
                    return template_sections[best_idx]
            except Exception as e:
                print(f"  ⚠️  Semantic matching failed: {e}")
        
        # Step 4: Rule-based synonym matching (fallback)
        for template_section, synonyms in self.section_synonyms.items():
            if candidate_clean in synonyms:
                # Find the matching template section
                for ts in template_sections:
                    if template_section.lower() in ts.lower():
                        print(f"  📋 Rule-based match: '{candidate_heading}' → '{ts}'")
                        return ts
        
        print(f"  ❌ No match found for: '{candidate_heading}'")
        return None
    
    def classify_unheaded_content(self, text: str, position_index: int = 0,
                                  template_sections: List[str] = None) -> Optional[str]:
        """
        Classify a paragraph without a heading to determine its section type.
        
        Args:
            text: The paragraph content
            position_index: Position in document (0 = first paragraph)
            template_sections: Available template sections
            
        Returns:
            Predicted section name, or None if uncertain
        """
        if not text or len(text.strip()) < 10:
            return None
        
        text_lower = text.lower()
        
        # Rule 1: Position-based (summary usually at top)
        if position_index <= 2 and len(text.split()) < 100:
            if any(word in text_lower for word in ['seeking', 'professional', 'experienced', 'motivated']):
                return 'SUMMARY'
        
        # Rule 2: Entity-based classification using spaCy
        if self.nlp is not None:
            try:
                doc = self.nlp(text[:500])  # Limit to first 500 chars for speed
                
                has_dates = any(ent.label_ == "DATE" for ent in doc.ents)
                has_orgs = any(ent.label_ == "ORG" for ent in doc.ents)
                has_gpe = any(ent.label_ == "GPE" for ent in doc.ents)  # Geo-political entities
                
                if has_dates and has_orgs:
                    return 'EMPLOYMENT'
                elif any(word in text_lower for word in ['university', 'degree', 'graduated', 'gpa', 'bachelor', 'master']):
                    return 'EDUCATION'
            except Exception as e:
                print(f"  ⚠️  Entity extraction failed: {e}")
        
        # Rule 3: Keyword-based classification
        employment_keywords = ['worked', 'managed', 'developed', 'led', 'responsible', 'duties', 'role']
        education_keywords = ['university', 'college', 'degree', 'graduated', 'gpa', 'major']
        skills_keywords = ['proficient', 'skilled', 'expertise', 'technologies', 'programming']
        
        employment_score = sum(1 for kw in employment_keywords if kw in text_lower)
        education_score = sum(1 for kw in education_keywords if kw in text_lower)
        skills_score = sum(1 for kw in skills_keywords if kw in text_lower)
        
        scores = {
            'EMPLOYMENT': employment_score,
            'EDUCATION': education_score,
            'SKILLS': skills_score
        }
        
        max_score = max(scores.values())
        if max_score >= 2:  # At least 2 keywords matched
            predicted = max(scores, key=scores.get)
            print(f"  🎯 Content classified as: {predicted} (score: {max_score})")
            return predicted
        
        return None
    
    def batch_map_sections(self, candidate_sections: Dict[str, str],
                          template_sections: List[str]) -> Dict[str, str]:
        """
        Map multiple candidate sections to template sections in one batch.
        
        Args:
            candidate_sections: Dict of {heading: content} from candidate resume
            template_sections: List of valid template section names
            
        Returns:
            Dict of {template_section: content} with mapped sections
        """
        mapped = {}
        
        for heading, content in candidate_sections.items():
            if heading:
                # Has heading - use intelligent mapping
                mapped_name = self.map_section(heading, template_sections)
                if mapped_name:
                    mapped[mapped_name] = content
                else:
                    # Try content classification as fallback
                    classified = self.classify_unheaded_content(content, 0, template_sections)
                    if classified:
                        mapped[classified] = content
            else:
                # No heading - classify by content
                classified = self.classify_unheaded_content(content, 0, template_sections)
                if classified:
                    mapped[classified] = content
        
        return mapped


# Singleton instance for reuse across requests
_mapper_instance = None

def get_section_mapper() -> SmartSectionMapper:
    """Get or create the singleton section mapper instance"""
    global _mapper_instance
    if _mapper_instance is None:
        _mapper_instance = SmartSectionMapper()
    return _mapper_instance
