"""
LAYER 4: Content Validator
Validates content belongs to correct section and prevents cross-contamination
- Classifies each content block independently
- Detects misplaced content (e.g., education in skills section)
- Moves content to correct sections
- Filters truly mismatched content
"""

import re
from typing import Dict, List, Tuple, Optional
import numpy as np

# Optional: spaCy for NER
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


class ContentValidator:
    """Validates content matches assigned sections, prevents mixing"""

    # Content signatures for each section type
    CONTENT_SIGNATURES = {
        'EMPLOYMENT': {
            'required_patterns': [
                r'\b(managed|developed|led|created|implemented|designed|built|responsible)\b',
                r'\b(company|corporation|team|project|product)\b',
            ],
            'positive_keywords': [
                'managed', 'developed', 'led', 'created', 'implemented', 'designed',
                'built', 'responsible', 'achieved', 'increased', 'improved', 'reduced',
                'collaborated', 'coordinated', 'delivered', 'established', 'maintained'
            ],
            'negative_keywords': [
                'bachelor', 'master', 'phd', 'degree', 'university', 'college',
                'gpa', 'graduated', 'coursework'
            ],
            'entity_types': ['ORG', 'DATE'],
            'min_entities': {'ORG': 1}
        },
        'EDUCATION': {
            'required_patterns': [
                r'\b(bachelor|master|phd|b\.s\.|m\.s\.|b\.a\.|m\.a\.|b\.tech|m\.tech|degree)\b',
                r'\b(university|college|institute|school)\b',
            ],
            'positive_keywords': [
                'bachelor', 'master', 'phd', 'doctorate', 'degree', 'university', 'college',
                'graduated', 'gpa', 'honors', 'cum laude', 'summa', 'magna', 'diploma', 'certificate',
                'coursework', 'thesis', 'dissertation', 'academic', 'student', 'scholar',
                'major', 'minor', 'concentration', 'education', 'school', 'institute'
            ],
            'negative_keywords': [
                'managed team', 'developed product', 'implemented solution', 'led project',
                'company', 'corporation', 'responsibilities', 'duties', 'position', 'role',
                'achieved', 'increased revenue', 'improved performance', 'reduced cost',
                'collaborated with', 'reported to', 'supervised'
            ],
            'entity_types': ['ORG', 'DATE'],
            'min_entities': {},
            'strong_negative_weight': 5.0  # Heavy penalty for employment keywords in education
        },
        'SKILLS': {
            'required_patterns': [],
            'positive_keywords': [
                'python', 'java', 'javascript', 'c++', 'sql', 'html', 'css',
                'react', 'angular', 'node', 'aws', 'azure', 'docker', 'kubernetes',
                'git', 'linux', 'windows', 'api', 'rest', 'graphql', 'mongodb',
                'postgresql', 'mysql', 'agile', 'scrum', 'ci/cd'
            ],
            'negative_keywords': [
                'bachelor', 'master', 'university', 'graduated', 'gpa',
                'managed', 'developed', 'led', 'responsibilities'
            ],
            'entity_types': [],
            'format': 'list',  # Skills are usually list-like
            'min_entities': {}
        },
        'SUMMARY': {
            'required_patterns': [],
            'positive_keywords': [
                'years of experience', 'professional', 'expertise', 'specialized',
                'passionate', 'dedicated', 'seeking', 'objective', 'goal'
            ],
            'negative_keywords': [],
            'entity_types': [],
            'format': 'paragraph',  # Summary is paragraph-style
            'min_entities': {}
        },
        'PROJECTS': {
            'required_patterns': [
                r'\b(project|developed|built|created|implemented)\b'
            ],
            'positive_keywords': [
                'project', 'developed', 'built', 'created', 'implemented',
                'application', 'website', 'system', 'tool', 'platform'
            ],
            'negative_keywords': [
                'bachelor', 'master', 'university', 'gpa'
            ],
            'entity_types': [],
            'min_entities': {}
        },
        'CERTIFICATIONS': {
            'required_patterns': [
                r'\b(certified|certification|license|credential)\b'
            ],
            'positive_keywords': [
                'certified', 'certification', 'license', 'credential',
                'aws', 'microsoft', 'cisco', 'google', 'oracle'
            ],
            'negative_keywords': [],
            'entity_types': ['ORG', 'DATE'],
            'min_entities': {}
        }
    }

    def __init__(self):
        # Load spaCy if available
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except:
                pass

    def validate_sections(self, sections: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """
        Main method: Validate all sections and fix cross-contamination

        Args:
            sections: Output from Layer 3 (section identifier)

        Returns:
            Validated and corrected sections
        """
        print("\n  [Layer 4] Validating content and preventing cross-contamination...")
        print(f"    [DEBUG] Input sections: {list(sections.keys())}")

        validated_sections = {}
        moved_content = []
        removed_content = []

        # Process each section
        for section_name, content_blocks in sections.items():
            print(f"\n    [DEBUG] Validating {section_name} section ({len(content_blocks)} blocks)...")

            if section_name not in validated_sections:
                validated_sections[section_name] = []

            block_num = 0
            for block in content_blocks:
                block_num += 1
                text = block.get('text', '')

                # Skip empty blocks
                if not text.strip():
                    continue

                # Validate: does this content belong in this section?
                is_valid, confidence, reason = self._validate_content(text, section_name)

                print(f"      [Block {block_num}] Confidence: {confidence:.2f} - {reason}")

                if is_valid and confidence >= 0.5:
                    # Content matches, keep in section
                    validated_sections[section_name].append(block)
                else:
                    # Content doesn't match! Find correct section
                    print(f"      ⚠ MISMATCH in {section_name}: '{text[:50]}...'")
                    print(f"      Confidence: {confidence:.2f}, Reason: {reason}")

                    correct_section = self._find_correct_section(text)

                    if correct_section and correct_section != section_name:
                        print(f"      💡 MOVING to {correct_section}")
                        if correct_section not in validated_sections:
                            validated_sections[correct_section] = []
                        validated_sections[correct_section].append(block)
                        moved_content.append({
                            'from': section_name,
                            'to': correct_section,
                            'text': text[:60]
                        })
                    else:
                        # Can't confidently classify - remove if confidence is very low
                        if confidence < 0.3:
                            print(f"      ❌ REMOVING low-confidence block")
                            removed_content.append({
                                'section': section_name,
                                'text': text[:60],
                                'confidence': confidence
                            })
                        else:
                            # Keep in original section but flag
                            block['validation_warning'] = reason
                            validated_sections[section_name].append(block)
                            print(f"      ⚠ KEEPING in {section_name} (flagged)")

        # Print validation summary
        print(f"\n    [VALIDATION SUMMARY]")
        if moved_content:
            print(f"    📊 Moved {len(moved_content)} misplaced blocks:")
            for move in moved_content:
                print(f"      {move['from']} → {move['to']}: {move['text']}...")

        if removed_content:
            print(f"    🗑️ Removed {len(removed_content)} low-confidence blocks:")
            for remove in removed_content:
                print(f"      From {remove['section']}: {remove['text']}... (conf: {remove['confidence']:.2f})")

        # Print final section sizes
        print(f"\n    [FINAL SECTIONS]:")
        for section, blocks in validated_sections.items():
            print(f"      {section}: {len(blocks)} blocks")

        return validated_sections

    def _validate_content(self, text: str, section_type: str) -> Tuple[bool, float, str]:
        """
        Validate if content matches expected section type

        Returns:
            (is_valid, confidence, reason)
        """
        if section_type not in self.CONTENT_SIGNATURES:
            return True, 1.0, "Unknown section type"

        signature = self.CONTENT_SIGNATURES[section_type]
        text_lower = text.lower()

        score = 0.0
        max_score = 0.0
        reasons = []

        # Check 1: Required patterns
        required_patterns = signature.get('required_patterns', [])
        if required_patterns:
            max_score += 2.0
            for pattern in required_patterns:
                if re.search(pattern, text_lower):
                    score += 2.0
                    reasons.append(f"has required pattern")
                    break

        # Check 2: Positive keywords
        positive_keywords = signature.get('positive_keywords', [])
        if positive_keywords:
            max_score += 3.0
            matches = sum(1 for kw in positive_keywords if kw in text_lower)
            if matches > 0:
                score += min(3.0, matches / 2)
                reasons.append(f"{matches} positive keywords")

        # Check 3: Negative keywords (should NOT be present)
        negative_keywords = signature.get('negative_keywords', [])
        strong_negative_weight = signature.get('strong_negative_weight', 1.0)
        if negative_keywords:
            max_score += 2.0 * strong_negative_weight
            neg_matches = sum(1 for kw in negative_keywords if kw in text_lower)
            if neg_matches == 0:
                score += 2.0 * strong_negative_weight
            else:
                # Apply heavy penalty for negative keywords
                score -= neg_matches * strong_negative_weight
                reasons.append(f"{neg_matches} NEGATIVE keywords found (major issue)")

        # Check 4: Format (list vs paragraph)
        expected_format = signature.get('format')
        if expected_format:
            max_score += 1.0
            is_list = ',' in text or '•' in text or '|' in text
            is_paragraph = len(text.split('.')) > 2

            if expected_format == 'list' and is_list:
                score += 1.0
                reasons.append("list format")
            elif expected_format == 'paragraph' and is_paragraph:
                score += 1.0
                reasons.append("paragraph format")

        # Check 5: Named entities (if spaCy available)
        if self.nlp and signature.get('entity_types'):
            max_score += 2.0
            try:
                doc = self.nlp(text[:500])
                required_entities = signature.get('min_entities', {})

                entities_found = {}
                for ent in doc.ents:
                    if ent.label_ not in entities_found:
                        entities_found[ent.label_] = 0
                    entities_found[ent.label_] += 1

                # Check if required entities are present
                has_required = all(
                    entities_found.get(ent_type, 0) >= min_count
                    for ent_type, min_count in required_entities.items()
                )

                if has_required:
                    score += 2.0
                    reasons.append("has required entities")
            except:
                pass

        # Calculate confidence
        if max_score > 0:
            confidence = score / max_score
        else:
            confidence = 1.0

        # Decision threshold
        is_valid = confidence >= 0.4  # 40% match threshold

        reason = ", ".join(reasons) if reasons else "no matching indicators"

        return is_valid, confidence, reason

    def _find_correct_section(self, text: str) -> Optional[str]:
        """
        Find the correct section for misplaced content

        Tests content against all section signatures
        Returns section with highest confidence
        """
        best_section = None
        best_confidence = 0.0

        for section_type in self.CONTENT_SIGNATURES.keys():
            is_valid, confidence, _ = self._validate_content(text, section_type)

            if confidence > best_confidence:
                best_confidence = confidence
                best_section = section_type

        # Only return if confidence is reasonable
        if best_confidence >= 0.5:
            return best_section

        return None

    def filter_mismatched_content(self, sections: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """
        Remove content that doesn't match any section well

        Use this for aggressive filtering
        """
        filtered_sections = {}

        for section_name, content_blocks in sections.items():
            filtered_blocks = []

            for block in content_blocks:
                text = block.get('text', '')

                # Check if content matches this section or any section
                is_valid, confidence, _ = self._validate_content(text, section_name)

                if is_valid or confidence >= 0.3:
                    filtered_blocks.append(block)
                else:
                    # Try to find if it matches ANY section
                    correct_section = self._find_correct_section(text)
                    if correct_section:
                        # Move to correct section
                        if correct_section not in filtered_sections:
                            filtered_sections[correct_section] = []
                        filtered_sections[correct_section].append(block)
                    else:
                        # Truly mismatched, skip
                        print(f"    ⚠ Filtering out low-confidence content: '{text[:40]}...'")

            if filtered_blocks:
                filtered_sections[section_name] = filtered_blocks

        return filtered_sections

    def check_content_duplication(self, sections: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """
        Detect and remove duplicate content across sections

        Returns: Deduplicated sections
        """
        seen_texts = set()
        deduped_sections = {}

        for section_name, content_blocks in sections.items():
            unique_blocks = []

            for block in content_blocks:
                text = block.get('text', '').strip()
                text_hash = hash(text[:100])  # Hash first 100 chars

                if text_hash not in seen_texts:
                    unique_blocks.append(block)
                    seen_texts.add(text_hash)
                else:
                    print(f"    ⏭ Skipping duplicate content in {section_name}")

            if unique_blocks:
                deduped_sections[section_name] = unique_blocks

        return deduped_sections


# Utility function
def validate_and_fix_sections(sections: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
    """Convenience function to validate sections"""
    validator = ContentValidator()
    validated = validator.validate_sections(sections)
    deduped = validator.check_content_duplication(validated)
    return deduped


if __name__ == "__main__":
    # Test with sample sections
    sample_sections = {
        'EMPLOYMENT': [
            {'text': 'Software Engineer at Google, 2020-2023'},
            {'text': 'Bachelor of Science in Computer Science, MIT'}  # WRONG SECTION!
        ],
        'EDUCATION': [
            {'text': 'Master of Science in AI, Stanford, 2020'}
        ],
        'SKILLS': [
            {'text': 'Python, Java, JavaScript, SQL, AWS, Docker'}
        ]
    }

    result = validate_and_fix_sections(sample_sections)
    print("\nValidated sections:")
    for section, content in result.items():
        print(f"\n{section}:")
        for block in content:
            print(f"  - {block['text']}")
