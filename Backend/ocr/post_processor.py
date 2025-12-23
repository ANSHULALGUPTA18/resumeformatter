"""
LAYER 7: Post-Processor
Final cleanup and quality assurance
- Cleans OCR artifacts
- Fixes common OCR errors
- Validates completeness
- Calculates quality scores
- Generates user feedback
"""

import re
from typing import Dict, List, Tuple


class PostProcessor:
    """Final processing and quality validation"""

    # Common OCR error corrections
    OCR_CORRECTIONS = {
        # Letter/number confusions
        r'\bl\b': 'I',  # Standalone lowercase L to I
        r'\bO\b(?=\d)': '0',  # Letter O before digit to zero
        r'(?<=\d)O\b': '0',  # Letter O after digit to zero
        r'(?<=[A-Z])0(?=[A-Z])': 'O',  # Zero between caps to O
        r'\b5(?=\w{2,})': 'S',  # 5 at start of word to S
        r'\b8(?=\w{2,})': 'B',  # 8 at start of word to B

        # Common word errors
        r'\bwa5\b': 'was',
        r'\bh4s\b': 'has',
        r'\b4nd\b': 'and',
        r'\bth3\b': 'the',
        r'\bc4n\b': 'can',

        # Spacing issues
        r'\s{2,}': ' ',  # Multiple spaces to single
        r'\n{3,}': '\n\n',  # Multiple newlines to double
    }

    def __init__(self):
        pass

    def process_final_output(self, mapped_data: Dict) -> Dict:
        """
        Main method: Final processing and validation

        Args:
            mapped_data: Output from Layer 6 (template mapper)

        Returns:
            {
                'candidate_info': {...},
                'sections': {...},
                'quality_scores': {...},
                'warnings': [...],
                'recommendations': [...]
            }
        """
        print("\n  [Layer 7] Post-processing and quality validation...")

        # Clean text in all fields
        cleaned_data = self._clean_all_text(mapped_data)

        # Validate completeness
        completeness = self._validate_completeness(cleaned_data)

        # Calculate quality scores
        quality_scores = self._calculate_quality_scores(cleaned_data, completeness)

        # Generate warnings and recommendations
        warnings, recommendations = self._generate_feedback(cleaned_data, quality_scores)

        # Cross-reference validation
        cross_ref_issues = self._cross_reference_validation(cleaned_data)
        warnings.extend(cross_ref_issues)

        print(f"    Overall Quality Score: {quality_scores['overall']:.1%}")

        return {
            'candidate_info': cleaned_data.get('candidate_info', {}),
            'sections': cleaned_data.get('sections', {}),
            'metadata': cleaned_data.get('metadata', {}),
            'quality_scores': quality_scores,
            'completeness': completeness,
            'warnings': warnings,
            'recommendations': recommendations
        }

    def _clean_all_text(self, data: Dict) -> Dict:
        """Clean all text fields in the data"""
        cleaned = {}

        # Clean candidate info
        if 'candidate_info' in data:
            cleaned['candidate_info'] = {}
            for key, value in data['candidate_info'].items():
                if isinstance(value, str):
                    cleaned['candidate_info'][key] = self._clean_text(value)
                else:
                    cleaned['candidate_info'][key] = value

        # Clean sections
        if 'sections' in data:
            cleaned['sections'] = {}
            for section_name, content in data['sections'].items():
                if isinstance(content, str):
                    cleaned['sections'][section_name] = self._clean_text(content)
                else:
                    cleaned['sections'][section_name] = content

        # Copy metadata
        if 'metadata' in data:
            cleaned['metadata'] = data['metadata']

        return cleaned

    def _clean_text(self, text: str) -> str:
        """Clean individual text field"""
        if not text:
            return text

        # Apply OCR corrections
        cleaned = text
        for pattern, replacement in self.OCR_CORRECTIONS.items():
            cleaned = re.sub(pattern, replacement, cleaned)

        # Fix broken words (hyphenation)
        cleaned = re.sub(r'(\w+)-\s+(\w+)', r'\1\2', cleaned)

        # Fix capitalization issues
        cleaned = self._fix_capitalization(cleaned)

        # Remove trailing/leading whitespace
        cleaned = cleaned.strip()

        return cleaned

    def _fix_capitalization(self, text: str) -> str:
        """Fix common capitalization issues"""
        # This is a simple implementation
        # More sophisticated rules can be added

        # Don't change if it's all caps (might be intentional like SKILLS)
        if text.isupper():
            return text

        # Fix sentences (capitalize after period)
        sentences = text.split('. ')
        fixed_sentences = []
        for sent in sentences:
            if sent:
                # Capitalize first letter
                sent = sent[0].upper() + sent[1:] if len(sent) > 1 else sent.upper()
            fixed_sentences.append(sent)

        return '. '.join(fixed_sentences)

    def _validate_completeness(self, data: Dict) -> Dict:
        """Check which required fields are present"""
        completeness = {}

        # Check candidate info
        candidate_info = data.get('candidate_info', {})
        completeness['name'] = bool(candidate_info.get('name'))
        completeness['email'] = bool(candidate_info.get('email'))
        completeness['phone'] = bool(candidate_info.get('phone'))
        completeness['contact_info'] = (
            completeness['email'] or completeness['phone']
        )

        # Check sections
        sections = data.get('sections', {})
        completeness['employment'] = bool(sections.get('EMPLOYMENT'))
        completeness['education'] = bool(sections.get('EDUCATION'))
        completeness['skills'] = bool(sections.get('SKILLS'))
        completeness['summary'] = bool(sections.get('SUMMARY'))

        # Required fields present
        required_fields = ['name', 'contact_info', 'employment', 'education']
        completeness['required_fields_present'] = all(
            completeness.get(field, False) for field in required_fields
        )

        return completeness

    def _calculate_quality_scores(self, data: Dict, completeness: Dict) -> Dict:
        """Calculate quality scores for different aspects"""
        scores = {}

        # Name confidence (based on completeness and length)
        name = data.get('candidate_info', {}).get('name', '')
        if name:
            word_count = len(name.split())
            if 2 <= word_count <= 4:
                scores['name'] = 0.95
            elif word_count == 1:
                scores['name'] = 0.5
            else:
                scores['name'] = 0.7
        else:
            scores['name'] = 0.0

        # Contact info confidence
        contact_count = sum([
            1 for field in ['email', 'phone', 'linkedin']
            if data.get('candidate_info', {}).get(field)
        ])
        scores['contact'] = min(1.0, contact_count / 2)  # 2+ contacts = 100%

        # Section scores
        sections = data.get('sections', {})
        for section_name in ['EMPLOYMENT', 'EDUCATION', 'SKILLS', 'SUMMARY']:
            content = sections.get(section_name, '')
            if content:
                # Score based on content length
                word_count = len(content.split())
                if word_count > 20:
                    scores[section_name.lower()] = 0.9
                elif word_count > 5:
                    scores[section_name.lower()] = 0.7
                else:
                    scores[section_name.lower()] = 0.5
            else:
                scores[section_name.lower()] = 0.0

        # Overall score (weighted average)
        weights = {
            'name': 0.25,
            'contact': 0.15,
            'employment': 0.25,
            'education': 0.20,
            'skills': 0.10,
            'summary': 0.05
        }

        overall = sum(
            scores.get(key, 0) * weight
            for key, weight in weights.items()
        )
        scores['overall'] = overall

        return scores

    def _generate_feedback(self, data: Dict, quality_scores: Dict) -> Tuple[List[str], List[str]]:
        """Generate warnings and recommendations"""
        warnings = []
        recommendations = []

        # Check name
        if quality_scores['name'] < 0.6:
            warnings.append("Candidate name may be incomplete or unclear")
            recommendations.append("Please verify the candidate name manually")

        # Check contact
        if quality_scores['contact'] < 0.5:
            warnings.append("Limited contact information extracted")
            recommendations.append("Please add email or phone number manually")

        # Check employment
        if quality_scores.get('employment', 0) < 0.5:
            warnings.append("Employment section may be incomplete")
            recommendations.append("Please review and complete employment history")

        # Check education
        if quality_scores.get('education', 0) < 0.5:
            warnings.append("Education section may be incomplete")
            recommendations.append("Please review and complete education details")

        # Overall quality
        if quality_scores['overall'] < 0.6:
            warnings.append("Overall extraction quality is low")
            recommendations.append("Manual review and editing strongly recommended")
        elif quality_scores['overall'] < 0.8:
            recommendations.append("Please verify all sections for accuracy")

        return warnings, recommendations

    def _cross_reference_validation(self, data: Dict) -> List[str]:
        """Cross-reference validation to catch logic errors"""
        issues = []

        # Check if sections are unusually short
        sections = data.get('sections', {})
        for section_name, content in sections.items():
            if content and len(content.split()) < 5:
                issues.append(f"{section_name} section is very short - may be incomplete")

        # Check for duplicate content across sections
        section_texts = [content for content in sections.values() if content]
        for i, text1 in enumerate(section_texts):
            for text2 in section_texts[i+1:]:
                # Check for substantial overlap
                if len(text1) > 50 and len(text2) > 50:
                    # Simple overlap check (first 50 chars)
                    if text1[:50] == text2[:50]:
                        issues.append("Potential duplicate content detected across sections")
                        break

        return issues

    def generate_user_report(self, processed_data: Dict) -> str:
        """Generate user-friendly report"""
        report = []
        report.append("="*60)
        report.append("OCR EXTRACTION REPORT")
        report.append("="*60)

        # Quality overview
        quality = processed_data['quality_scores']['overall']
        if quality >= 0.8:
            status = "✓ HIGH QUALITY"
        elif quality >= 0.6:
            status = "⚠ MEDIUM QUALITY - Review recommended"
        else:
            status = "⚠ LOW QUALITY - Manual review required"

        report.append(f"\nOverall Quality: {quality:.1%} - {status}")

        # Field scores
        report.append("\nField Confidence Scores:")
        scores = processed_data['quality_scores']
        for field in ['name', 'contact', 'employment', 'education', 'skills']:
            if field in scores:
                score = scores[field]
                indicator = "✓" if score >= 0.7 else "⚠"
                report.append(f"  {indicator} {field.title()}: {score:.1%}")

        # Warnings
        if processed_data['warnings']:
            report.append("\n⚠ Warnings:")
            for warning in processed_data['warnings']:
                report.append(f"  - {warning}")

        # Recommendations
        if processed_data['recommendations']:
            report.append("\nRecommendations:")
            for rec in processed_data['recommendations']:
                report.append(f"  - {rec}")

        report.append("\n" + "="*60)

        return '\n'.join(report)


# Utility function
def post_process_output(mapped_data: Dict) -> Dict:
    """Convenience function for post-processing"""
    processor = PostProcessor()
    return processor.process_final_output(mapped_data)


if __name__ == "__main__":
    # Test with sample data
    sample_data = {
        'candidate_info': {
            'name': 'J0HN D0E',  # OCR errors
            'email': 'john.doe@email.com',
            'phone': '(555) 123-4567'
        },
        'sections': {
            'EMPLOYMENT': 'S0ftware  Engineer at Google',  # OCR errors
            'EDUCATION': 'Bachelor of Science',
            'SKILLS': 'Python, Java'
        }
    }

    result = post_process_output(sample_data)
    processor = PostProcessor()
    print(processor.generate_user_report(result))
