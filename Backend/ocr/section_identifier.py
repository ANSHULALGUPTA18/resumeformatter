"""
LAYER 3: Intelligent Section Identifier
Identifies resume sections even with OCR errors and missing headers
- Fuzzy matching for section headers (handles OCR errors)
- Content-based classification for headerless sections
- Semantic similarity matching
- Section boundary detection
"""

import re
from typing import List, Dict, Optional, Tuple
from fuzzywuzzy import fuzz, process
import numpy as np

# Optional: Sentence transformers for semantic matching
try:
    from sentence_transformers import SentenceTransformer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Optional: spaCy for NER
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


class SectionIdentifier:
    """Identifies resume sections from OCR output"""

    # Standard section mappings
    SECTION_MAPPINGS = {
        'EMPLOYMENT': [
            'employment', 'employment history', 'work experience', 'professional experience',
            'work history', 'career history', 'experience', 'professional background',
            'relevant employment', 'career experience', 'work', 'jobs', 'positions',
            'professional summary', 'work record'
        ],
        'EDUCATION': [
            'education', 'educational background', 'academic background',
            'academic qualifications', 'qualifications', 'academics',
            'education background', 'schooling', 'degrees', 'academic history'
        ],
        'SKILLS': [
            'skills', 'technical skills', 'core competencies', 'key skills',
            'professional skills', 'areas of expertise', 'competencies',
            'skill set', 'expertise', 'technical competencies', 'technologies',
            'technical proficiencies', 'core skills'
        ],
        'SUMMARY': [
            'summary', 'professional summary', 'career summary', 'profile',
            'professional profile', 'career objective', 'objective',
            'executive summary', 'career overview', 'about me', 'about', 'overview'
        ],
        'PROJECTS': [
            'projects', 'key projects', 'project experience', 'notable projects',
            'portfolio', 'selected projects', 'project work'
        ],
        'CERTIFICATIONS': [
            'certifications', 'certificates', 'professional certifications',
            'licenses', 'credentials', 'certified', 'licensing', 'professional licenses'
        ],
        'ACHIEVEMENTS': [
            'achievements', 'awards', 'honors', 'recognition', 'accomplishments',
            'awards and honors', 'distinctions'
        ],
        'LANGUAGES': [
            'languages', 'language skills', 'language proficiency', 'linguistic skills'
        ]
    }

    def __init__(self):
        # Load semantic model if available
        self.model = None
        if TRANSFORMERS_AVAILABLE:
            try:
                print("  Loading sentence transformer model...")
                self.model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
            except Exception as e:
                print(f"  Warning: Could not load sentence transformer: {e}")

        # Load spaCy if available
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except:
                print("  Warning: spaCy model not loaded. Install with: python -m spacy download en_core_web_sm")

    def identify_sections(self, ocr_results: Dict) -> Dict[str, List[Dict]]:
        """
        Main method: Identify sections from OCR results

        Args:
            ocr_results: Output from Layer 2 (Multi-Pass OCR)

        Returns:
            {
                'EMPLOYMENT': [...content blocks...],
                'EDUCATION': [...content blocks...],
                'SKILLS': [...content blocks...],
                ...
            }
        """
        print("\n  [Layer 3] Identifying sections with strict boundaries...")

        # Extract section headers and body content
        section_headers = ocr_results.get('section_headers_ocr', [])
        body_content = ocr_results.get('body_ocr', [])

        print(f"    [DEBUG] Found {len(section_headers)} section headers")
        print(f"    [DEBUG] Found {len(body_content)} body blocks")

        # Debug: Print all detected headers
        for i, header in enumerate(section_headers):
            print(f"    [DEBUG] Header {i}: '{header['text'][:50]}'")

        # Step 1: Match headers to standard sections
        matched_sections = {}
        unmatched_content = []

        current_section = None
        current_content = []

        # Combine headers and body, sort by position
        all_blocks = []
        for header in section_headers:
            all_blocks.append({
                'type': 'header',
                'text': header['text'],
                'y': header['original_bbox'][1],
                'data': header
            })

        for body in body_content:
            all_blocks.append({
                'type': 'body',
                'text': body['text'],
                'y': body['original_bbox'][1],
                'data': body
            })

        # Sort by vertical position (top to bottom)
        all_blocks.sort(key=lambda x: x['y'])

        print(f"    [DEBUG] Processing {len(all_blocks)} blocks in reading order...")

        # Process blocks in order
        for idx, block in enumerate(all_blocks):
            if block['type'] == 'header':
                # Save previous section content first
                if current_section and current_content:
                    if current_section not in matched_sections:
                        matched_sections[current_section] = []
                    matched_sections[current_section].extend(current_content)
                    print(f"    [DEBUG] Saved {len(current_content)} blocks to {current_section}")

                # Match this header to standard section
                matched_section = self._match_header_to_section(block['text'])

                if matched_section:
                    current_section = matched_section
                    current_content = []
                    print(f"    ✓ Matched '{block['text'][:40]}' → {matched_section}")
                else:
                    # Unmatched header - try content classification
                    print(f"    ⚠ Could not match header: '{block['text'][:40]}'")
                    classified = self._classify_content_by_analysis(block['text'])
                    if classified:
                        current_section = classified
                        current_content = []
                        print(f"    ✓ Classified as → {classified}")
                    else:
                        # Treat as content of current section
                        if current_section:
                            current_content.append(block)
                        else:
                            unmatched_content.append(block)

            elif block['type'] == 'body':
                # Validate content belongs to current section
                if current_section:
                    # Double-check: does this content actually belong here?
                    content_classification = self._classify_content_by_analysis(block['text'])

                    if content_classification and content_classification != current_section:
                        # Content doesn't match current section!
                        print(f"    [WARN] Block {idx} classified as {content_classification} but in {current_section} section")
                        print(f"    [WARN] Content preview: '{block['text'][:60]}'...")

                        # Add to correct section instead
                        if content_classification not in matched_sections:
                            matched_sections[content_classification] = []
                        matched_sections[content_classification].append(block)
                        print(f"    ✓ Moved to {content_classification}")
                    else:
                        # Content matches, add normally
                        current_content.append(block)
                else:
                    # No current section, classify by content
                    unmatched_content.append(block)

        # Save last section
        if current_section and current_content:
            if current_section not in matched_sections:
                matched_sections[current_section] = []
            matched_sections[current_section].extend(current_content)
            print(f"    [DEBUG] Saved {len(current_content)} blocks to {current_section} (final)")

        # Step 2: Classify unmatched content by content analysis
        print(f"    [DEBUG] Classifying {len(unmatched_content)} unmatched blocks...")
        for block in unmatched_content:
            classified_section = self._classify_content_by_analysis(block['text'])
            if classified_section:
                if classified_section not in matched_sections:
                    matched_sections[classified_section] = []
                matched_sections[classified_section].append(block)
                print(f"    🎯 Classified unheaded content → {classified_section}")

        # Print summary
        print(f"\n    [SUMMARY] Sections identified:")
        for section, blocks in matched_sections.items():
            print(f"      {section}: {len(blocks)} blocks")

        return matched_sections

    def _match_header_to_section(self, header_text: str) -> Optional[str]:
        """
        Match header text to standard section using multiple techniques

        Techniques (in priority order):
        1. Exact match
        2. Fuzzy match (handles OCR errors like EDUC4TION)
        3. Semantic similarity
        4. Rule-based patterns
        """
        header_clean = header_text.strip().lower()
        header_clean = re.sub(r'[^a-z\s]', '', header_clean)  # Remove special chars

        if not header_clean:
            return None

        # Technique 1: Exact match
        for section, synonyms in self.SECTION_MAPPINGS.items():
            if header_clean in synonyms:
                return section

        # Technique 2: Fuzzy matching (handles OCR errors)
        best_match = None
        best_score = 0

        for section, synonyms in self.SECTION_MAPPINGS.items():
            for synonym in synonyms:
                # Use token_sort_ratio for flexible matching
                score = fuzz.token_sort_ratio(header_clean, synonym)

                if score > best_score:
                    best_score = score
                    best_match = section

        # Accept fuzzy match if score > 80
        if best_score > 80:
            return best_match

        # Technique 3: Semantic similarity (if available)
        if self.model:
            try:
                header_emb = self.model.encode([header_clean])
                best_sim = 0
                best_section = None

                for section, synonyms in self.SECTION_MAPPINGS.items():
                    synonym_embs = self.model.encode(synonyms)
                    similarities = np.dot(header_emb, synonym_embs.T)[0]
                    max_sim = np.max(similarities)

                    if max_sim > best_sim:
                        best_sim = max_sim
                        best_section = section

                # Accept semantic match if similarity > 0.65
                if best_sim > 0.65:
                    return best_section
            except:
                pass

        # Technique 4: Rule-based keyword matching
        keyword_patterns = {
            'EMPLOYMENT': ['work', 'employ', 'job', 'career', 'position', 'company'],
            'EDUCATION': ['educat', 'school', 'university', 'college', 'degree', 'academic'],
            'SKILLS': ['skill', 'technolog', 'competenc', 'proficien', 'expertise'],
            'SUMMARY': ['summar', 'profile', 'objective', 'overview', 'about'],
            'PROJECTS': ['project', 'portfolio'],
            'CERTIFICATIONS': ['certif', 'license', 'credential'],
            'ACHIEVEMENTS': ['achieve', 'award', 'honor', 'recognition'],
            'LANGUAGES': ['language', 'linguistic']
        }

        for section, keywords in keyword_patterns.items():
            if any(kw in header_clean for kw in keywords):
                return section

        return None

    def _classify_content_by_analysis(self, content: str) -> Optional[str]:
        """
        Classify content without header using content analysis

        Analyzes:
        - Keywords and patterns (with priority scoring)
        - Named entities (ORG, EDU, DATE)
        - Sentence structure
        - List vs paragraph format
        """
        content_lower = content.lower()

        # Score-based classification to handle overlapping patterns
        scores = {'EDUCATION': 0, 'EMPLOYMENT': 0, 'SKILLS': 0, 'SUMMARY': 0, 'PROJECTS': 0}

        # ===== PRIORITY 1: Strong Education Indicators (highest weight) =====
        strong_education_patterns = [
            r'\b(bachelor|master|phd|doctorate|b\.s\.|m\.s\.|b\.a\.|m\.a\.|b\.tech|m\.tech)\b',
            r'\b(university|college)\b',
            r'\bgpa\s*[:\-]?\s*\d',
            r'\b(cum laude|magna cum laude|summa cum laude)\b',
            r'\b(thesis|dissertation)\b',
            r'\b(major|minor)\s*[:\-]',
            r'\b(academic)\b'
        ]
        education_matches = sum(1 for p in strong_education_patterns if re.search(p, content_lower))
        scores['EDUCATION'] += education_matches * 5  # High weight

        # Additional education keywords
        education_keywords = [
            'graduated', 'graduation', 'degree', 'diploma', 'school', 'institute',
            'coursework', 'honors', 'academic', 'student', 'education'
        ]
        education_kw_matches = sum(1 for kw in education_keywords if kw in content_lower)
        scores['EDUCATION'] += education_kw_matches * 2

        # ===== PRIORITY 2: Strong Employment Indicators =====
        # Only count as employment if NO strong education indicators
        if scores['EDUCATION'] < 5:
            strong_employment_patterns = [
                r'\b(company|corporation|inc\.|ltd\.|llc)\b',
                r'\b(position|title|role)\s*[:\-]',
                r'\b(responsibilities|duties)\s*[:\-]',
                r'\d+\s*(years?|months?)\s+(of\s+)?(work\s+)?experience',
                r'\b(achieved|increased|improved|reduced)\s+\d+%',
                r'\b(promoted|hired|recruited)\b',
                r'\b(employee|employer|worked at)\b'
            ]
            employment_matches = sum(1 for p in strong_employment_patterns if re.search(p, content_lower))
            scores['EMPLOYMENT'] += employment_matches * 4

            # Employment action verbs (only if no education context)
            employment_verbs = [
                'managed team', 'led team', 'supervised', 'coordinated team',
                'responsibilities included', 'duties included', 'reported to',
                'collaborated with', 'partnered with'
            ]
            employment_verb_matches = sum(1 for v in employment_verbs if v in content_lower)
            scores['EMPLOYMENT'] += employment_verb_matches * 3

        # If education score is high, return immediately (don't let employment override)
        if scores['EDUCATION'] >= 5:
            return 'EDUCATION'

        # If employment score is high, return
        if scores['EMPLOYMENT'] >= 8:
            return 'EMPLOYMENT'

        # ===== PRIORITY 3: Skills indicators =====
        skills_patterns = [
            ',' in content or '•' in content or '|' in content  # List format
        ]
        if any(skills_patterns):
            words = re.split(r'[,•|\n]', content)
            avg_words_per_item = np.mean([len(w.split()) for w in words if w.strip()])
            if avg_words_per_item < 4:  # Short phrases
                scores['SKILLS'] += 5

                # Check for technology keywords
                tech_keywords = [
                    'python', 'java', 'javascript', 'sql', 'aws', 'azure', 'docker',
                    'react', 'angular', 'node', 'api', 'database', 'cloud', 'agile',
                    'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin', 'typescript'
                ]
                tech_matches = sum(1 for kw in tech_keywords if kw in content_lower)
                scores['SKILLS'] += tech_matches * 2

        # ===== PRIORITY 4: Summary indicators =====
        summary_keywords = [
            'years of experience', 'professional', 'expertise in', 'specialized in',
            'seeking', 'passionate about', 'dedicated', 'experienced', 'background in'
        ]
        summary_matches = sum(1 for kw in summary_keywords if kw in content_lower)
        scores['SUMMARY'] += summary_matches * 3

        # Summary is usually narrative/paragraph style
        if not content.startswith('•') and not content.startswith('-'):
            sentences = content.split('.')
            if len(sentences) > 2:  # Multiple sentences
                scores['SUMMARY'] += 2

        # ===== PRIORITY 5: Projects indicators =====
        project_keywords = ['project', 'built application', 'developed application',
                           'created tool', 'implemented system']
        project_matches = sum(1 for kw in project_keywords if kw in content_lower)
        scores['PROJECTS'] += project_matches * 3

        # ===== Use NER for additional context (if available) =====
        if self.nlp:
            try:
                doc = self.nlp(content[:500])  # Analyze first 500 chars

                # Count entity types
                org_count = sum(1 for ent in doc.ents if ent.label_ == "ORG")
                date_count = sum(1 for ent in doc.ents if ent.label_ == "DATE")

                # Educational institutions in content
                edu_institutions = ['university', 'college', 'institute', 'school']
                has_edu_institution = any(inst in content_lower for inst in edu_institutions)

                # If has educational institution + dates, boost education score
                if has_edu_institution and date_count >= 1:
                    scores['EDUCATION'] += 5

                # If has company + dates but NO educational institution, boost employment
                elif org_count >= 1 and date_count >= 1 and not has_edu_institution:
                    scores['EMPLOYMENT'] += 3

            except:
                pass

        # Return section with highest score
        if max(scores.values()) > 0:
            best_section = max(scores, key=scores.get)
            return best_section

        return None

    def detect_section_boundaries(self, text_blocks: List[Dict]) -> List[Tuple[int, int, str]]:
        """
        Detect where sections begin and end

        Returns: List of (start_idx, end_idx, section_type)
        """
        boundaries = []
        current_section = None
        section_start = 0

        for i, block in enumerate(text_blocks):
            # Check if this block is a section header
            if block.get('is_heading', False):
                # Save previous section
                if current_section:
                    boundaries.append((section_start, i - 1, current_section))

                # Start new section
                matched_section = self._match_header_to_section(block['text'])
                if matched_section:
                    current_section = matched_section
                    section_start = i + 1

            # Check for content type change (section transition without header)
            elif i > 0 and current_section:
                prev_type = self._classify_content_by_analysis(text_blocks[i-1]['text'])
                curr_type = self._classify_content_by_analysis(block['text'])

                if prev_type and curr_type and prev_type != curr_type:
                    # Section changed
                    boundaries.append((section_start, i - 1, current_section))
                    current_section = curr_type
                    section_start = i

        # Save last section
        if current_section:
            boundaries.append((section_start, len(text_blocks) - 1, current_section))

        return boundaries


# Utility function
def identify_sections_from_ocr(ocr_results: Dict) -> Dict[str, List[Dict]]:
    """Convenience function to identify sections"""
    identifier = SectionIdentifier()
    return identifier.identify_sections(ocr_results)


if __name__ == "__main__":
    # Test with sample OCR results
    sample_ocr = {
        'section_headers_ocr': [
            {'text': 'WORK EXPERIENCE', 'original_bbox': (0, 100, 200, 30)},
            {'text': 'EDUC4TION', 'original_bbox': (0, 400, 200, 30)},  # OCR error
        ],
        'body_ocr': [
            {'text': 'Software Engineer at Google...', 'original_bbox': (0, 150, 400, 200)},
            {'text': 'Bachelor of Science in CS, MIT, 2020', 'original_bbox': (0, 450, 400, 50)},
        ]
    }

    result = identify_sections_from_ocr(sample_ocr)
    print("Identified sections:")
    for section, content in result.items():
        print(f"\n{section}:")
        for block in content:
            print(f"  - {block['text'][:60]}...")
