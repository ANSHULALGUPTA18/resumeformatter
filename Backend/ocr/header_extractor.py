"""
LAYER 5: Enhanced Header Extractor
Reliably extracts candidate name and contact information
- Multiple name extraction techniques (visual + NER + position)
- Robust contact info extraction (email, phone, LinkedIn, location)
- Fallback strategies for missing information
- Header reconstruction from fragments
"""

import re
from typing import Dict, List, Optional, Tuple

# Optional: spaCy for NER
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


class HeaderExtractor:
    """Extracts candidate name and contact information from resume header"""

    def __init__(self):
        # Load spaCy for NER
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except:
                print("  Warning: spaCy not loaded for NER")

        # Contact info patterns
        self.email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        self.phone_patterns = [
            r'\+?1?\s*\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}',  # US format
            r'\d{3}[\s.-]\d{3}[\s.-]\d{4}',  # 123-456-7890
            r'\(\d{3}\)\s*\d{3}[\s.-]\d{4}',  # (123) 456-7890
        ]
        self.linkedin_pattern = r'(linkedin\.com/in/[a-zA-Z0-9-]+|in/[a-zA-Z0-9-]+)'
        self.github_pattern = r'(github\.com/[a-zA-Z0-9-]+|@[a-zA-Z0-9-]+)'

    def extract_header_info(self, header_ocr: Dict, layout_info: Dict) -> Dict:
        """
        Main method: Extract complete header information

        Args:
            header_ocr: Header OCR result from Layer 2
            layout_info: Layout analysis from Layer 1

        Returns:
            {
                'name': str,
                'email': str,
                'phone': str,
                'linkedin': str,
                'github': str,
                'location': str,
                'title': str,
                'confidence': {name: float, contact: float}
            }
        """
        print("\n  [Layer 5] Extracting header information...")

        header_text = header_ocr.get('text', '')
        text_blocks = layout_info.get('text_blocks', [])

        # Get blocks from header zone
        header_blocks = [b for b in text_blocks if b.get('zone') == 'header']

        # Extract name
        name, name_confidence = self._extract_name(header_text, header_blocks)
        print(f"    Name: {name} (confidence: {name_confidence:.1%})")

        # Extract contact information
        email = self._extract_email(header_text)
        phone = self._extract_phone(header_text)
        linkedin = self._extract_linkedin(header_text)
        github = self._extract_github(header_text)
        location = self._extract_location(header_text)

        # Extract title (job title if present)
        title = self._extract_title(header_text, header_blocks, name)

        # Calculate overall contact confidence
        contact_confidence = self._calculate_contact_confidence(email, phone, linkedin)

        return {
            'name': name or '',
            'email': email or '',
            'phone': phone or '',
            'linkedin': linkedin or '',
            'github': github or '',
            'location': location or '',
            'title': title or '',
            'confidence': {
                'name': name_confidence,
                'contact': contact_confidence
            }
        }

    def _extract_name(self, header_text: str, header_blocks: List[Dict]) -> Tuple[str, float]:
        """
        Extract candidate name using multiple techniques

        Priority:
        1. Largest text in header zone (visual)
        2. PERSON entity (NER)
        3. First non-contact line
        4. Email prefix fallback
        """
        lines = [line.strip() for line in header_text.split('\n') if line.strip()]

        # Technique 1: Find largest text block in header
        if header_blocks:
            # Sort by height (largest first)
            sorted_blocks = sorted(header_blocks, key=lambda b: b.get('height', 0), reverse=True)

            for block in sorted_blocks[:3]:  # Check top 3 largest
                text = block.get('text', '').strip()

                # Skip if it's contact info
                if self._is_contact_info(text):
                    continue

                # Skip if too many words (likely a summary)
                if len(text.split()) > 5:
                    continue

                # This is likely the name
                return self._clean_name(text), 0.9

        # Technique 2: Use NER to find PERSON entity
        if self.nlp:
            try:
                doc = self.nlp(header_text[:500])
                persons = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]

                if persons:
                    # Use first person entity found
                    name = persons[0]
                    # Validate: should be 2-4 words
                    if 2 <= len(name.split()) <= 4:
                        return self._clean_name(name), 0.85
            except:
                pass

        # Technique 3: First non-contact line
        for line in lines[:5]:  # Check first 5 lines
            if self._is_contact_info(line):
                continue

            # Should be relatively short
            if len(line.split()) <= 5:
                # Could be name
                if self._looks_like_name(line):
                    return self._clean_name(line), 0.7

        # Technique 4: Fallback - extract from email
        email_match = re.search(self.email_pattern, header_text)
        if email_match:
            email = email_match.group(0)
            name_part = email.split('@')[0]
            # Convert john.smith or john_smith to John Smith
            name = name_part.replace('.', ' ').replace('_', ' ').title()
            return name, 0.5

        # Technique 5: Use first line as last resort
        if lines:
            return self._clean_name(lines[0]), 0.3

        return '', 0.0

    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address"""
        match = re.search(self.email_pattern, text)
        if match:
            email = match.group(0)
            print(f"    Email: {email}")
            return email
        return None

    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number"""
        for pattern in self.phone_patterns:
            match = re.search(pattern, text)
            if match:
                phone = match.group(0)
                # Normalize format
                phone = self._normalize_phone(phone)
                print(f"    Phone: {phone}")
                return phone
        return None

    def _extract_linkedin(self, text: str) -> Optional[str]:
        """Extract LinkedIn URL"""
        match = re.search(self.linkedin_pattern, text, re.IGNORECASE)
        if match:
            linkedin = match.group(0)
            # Ensure full URL
            if not linkedin.startswith('http'):
                if linkedin.startswith('in/'):
                    linkedin = 'linkedin.com/' + linkedin
                if not linkedin.startswith('linkedin.com'):
                    linkedin = 'linkedin.com/in/' + linkedin.split('/')[-1]
            print(f"    LinkedIn: {linkedin}")
            return linkedin
        return None

    def _extract_github(self, text: str) -> Optional[str]:
        """Extract GitHub URL"""
        match = re.search(self.github_pattern, text, re.IGNORECASE)
        if match:
            github = match.group(0)
            print(f"    GitHub: {github}")
            return github
        return None

    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location (City, State)"""
        # Pattern: City, ST or City, State
        location_pattern = r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*),\s*([A-Z]{2}|[A-Z][a-z]+)\b'
        match = re.search(location_pattern, text)
        if match:
            location = match.group(0)
            print(f"    Location: {location}")
            return location

        # Use NER if available
        if self.nlp:
            try:
                doc = self.nlp(text[:500])
                gpe_entities = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
                if gpe_entities:
                    location = ", ".join(gpe_entities[:2])  # City, State
                    return location
            except:
                pass

        return None

    def _extract_title(self, header_text: str, header_blocks: List[Dict], name: str) -> Optional[str]:
        """Extract job title (if present below name)"""
        lines = [line.strip() for line in header_text.split('\n') if line.strip()]

        # Find line with name
        name_line_idx = -1
        for i, line in enumerate(lines):
            if name and name.lower() in line.lower():
                name_line_idx = i
                break

        # Check next line after name
        if name_line_idx >= 0 and name_line_idx < len(lines) - 1:
            potential_title = lines[name_line_idx + 1]

            # Skip if it's contact info
            if self._is_contact_info(potential_title):
                return None

            # Should be reasonably short (job titles are 2-8 words)
            if 2 <= len(potential_title.split()) <= 8:
                # Common title keywords
                title_keywords = [
                    'engineer', 'developer', 'manager', 'analyst', 'specialist',
                    'consultant', 'architect', 'designer', 'scientist', 'lead',
                    'senior', 'junior', 'principal', 'staff', 'director'
                ]
                if any(kw in potential_title.lower() for kw in title_keywords):
                    return potential_title

        return None

    def _is_contact_info(self, text: str) -> bool:
        """Check if text contains contact information"""
        text_lower = text.lower()
        contact_indicators = [
            '@',  # Email
            'phone', 'tel', 'mobile', 'cell',
            'linkedin', 'github',
            'http://', 'https://',
            '(' in text and ')' in text,  # Phone with parens
        ]
        return any(indicator in text_lower if isinstance(indicator, str) else indicator
                   for indicator in contact_indicators)

    def _looks_like_name(self, text: str) -> bool:
        """Check if text looks like a name"""
        # Should be 2-4 words
        words = text.split()
        if not (2 <= len(words) <= 4):
            return False

        # Each word should be title case or all caps
        for word in words:
            if not (word[0].isupper() if word else False):
                return False

        # Should not contain numbers
        if re.search(r'\d', text):
            return False

        return True

    def _clean_name(self, name: str) -> str:
        """Clean and format name properly"""
        # Remove extra whitespace
        name = ' '.join(name.split())

        # Remove common prefixes/suffixes
        suffixes = ['jr', 'sr', 'ii', 'iii', 'iv']
        words = name.split()
        cleaned_words = [w for w in words if w.lower() not in suffixes or len(words) <= 2]

        name = ' '.join(cleaned_words)

        # Ensure title case
        name = name.title()

        return name

    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number to consistent format"""
        # Extract digits only
        digits = re.sub(r'\D', '', phone)

        # Format as (XXX) XXX-XXXX
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        else:
            return phone  # Return as-is if format is unclear

    def _calculate_contact_confidence(self, email: Optional[str],
                                     phone: Optional[str],
                                     linkedin: Optional[str]) -> float:
        """Calculate confidence based on extracted contact info"""
        found_count = sum([1 for x in [email, phone, linkedin] if x])

        if found_count >= 2:
            return 0.95
        elif found_count == 1:
            return 0.7
        else:
            return 0.3


# Utility function
def extract_header_information(header_ocr: Dict, layout_info: Dict) -> Dict:
    """Convenience function to extract header info"""
    extractor = HeaderExtractor()
    return extractor.extract_header_info(header_ocr, layout_info)


if __name__ == "__main__":
    # Test with sample header
    sample_header = {
        'text': 'JOHN DOE\nSenior Software Engineer\njohn.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe\nSan Francisco, CA'
    }

    sample_layout = {
        'text_blocks': [
            {'text': 'JOHN DOE', 'zone': 'header', 'height': 24},
            {'text': 'Senior Software Engineer', 'zone': 'header', 'height': 14},
            {'text': 'john.doe@email.com | (555) 123-4567', 'zone': 'header', 'height': 10}
        ]
    }

    result = extract_header_information(sample_header, sample_layout)
    print("\nExtracted header:")
    for key, value in result.items():
        if key != 'confidence':
            print(f"  {key}: {value}")
    print(f"  Confidence: {result['confidence']}")
