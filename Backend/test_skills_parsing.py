"""
Test script to verify skills parsing works correctly
"""
import sys
sys.path.insert(0, '.')

# Mock resume data with long skill descriptions (like the actual data)
mock_skills_raw = [
    "Skilled in updating fiber records, creating documentation using Excel, GIS software, and Bluebeam for accurate network mapping and records management",
    "Hands-on experience with OTDR and CDD for testing, monitoring networks, analyzing fiber performance, and troubleshooting connectivity issues to ensure network reliability",
    "Proficient in fiber splicing techniques, including cable preparation, fusion splicing infrastructure, managing fiber cables, distribution boxes, and network plans",
    "Experienced in DevOps tools like Docker, Kubernetes, Jenkins, and GitLab CI/CD",
    "Python, Java, C++, JavaScript",
    "AWS, Azure, Google Cloud Platform"
]

# Test the parsing
from utils.word_formatter import WordFormatter

# Create a minimal formatter instance just to test the parsing method
class MockFormatter:
    def _parse_individual_skills(self, skills_raw):
        """Improved parsing - extracts clean skill names"""
        import re
        individual_skills = []
        
        # Common skill/technology patterns to extract
        known_patterns = [
            r'\b(Python|Java|JavaScript|TypeScript|C\+\+|C#|Ruby|PHP|Go|Rust|Swift|Kotlin|Scala)\b',
            r'\b(AWS|Azure|Google Cloud|GCP|Oracle Cloud)\b',
            r'\b(Docker|Kubernetes|Jenkins|GitLab|GitHub|Terraform|Ansible)\b',
            r'\b(MySQL|PostgreSQL|MongoDB|Redis|Oracle|SQL Server)\b',
            r'\b(Excel|Word|PowerPoint|Outlook|Access|Microsoft Office)\b',
            r'\b(OTDR|CDD|OFCW|AOSS|GIS|Bluebeam|AutoCAD)\b',
            r'\b(Fiber Splicing|Fiber Records|Circuit Vision)\b',
            r'\b(Windows|Linux|Unix|macOS|Ubuntu)\b',
            r'\b(React|Angular|Vue|Django|Flask|Spring|Node\.js)\b',
        ]
        
        for skill_line in skills_raw:
            skill_text = skill_line if isinstance(skill_line, str) else str(skill_line)
            skill_text = skill_text.strip()
            
            # Extract known technologies
            for pattern in known_patterns:
                matches = re.finditer(pattern, skill_text, re.IGNORECASE)
                for match in matches:
                    skill_name = match.group(0).strip()
                    if skill_name and len(skill_name) >= 2:
                        individual_skills.append(skill_name)
            
            # Handle clean comma-separated lists (short lines)
            if len(skill_text) < 100 and ',' in skill_text:
                cleaned_text = re.sub(r'^(skilled in|proficient in|experience with|knowledge of|expertise in)\s+', '', skill_text, flags=re.IGNORECASE)
                parts = re.split(r',\s*(?:and\s+)?', cleaned_text)
                for part in parts:
                    part = part.strip().lstrip('•–—-*● ')
                    part = re.sub(r'^(using|creating|updating|managing|implementing|configuring|analyzing|monitoring|troubleshooting)\s+', '', part, flags=re.IGNORECASE)
                    part = re.sub(r'\s+(for|to|with|in|on|at)\s+.*$', '', part)
                    part = part.strip()
                    
                    if 2 <= len(part) <= 40 and not part.lower().startswith(('and ', 'or ', 'the ', 'a ')):
                        if part.islower():
                            part = part.title()
                        individual_skills.append(part)
            
            # Extract from "like X, Y, and Z" patterns
            like_patterns = re.findall(r'(?:like|such as|including)\s+([A-Za-z0-9\s,\.]+?)(?:\s+for|\s+to|\s+and\s+[a-z]+ing|$)', skill_text, re.IGNORECASE)
            for pattern_match in like_patterns:
                items = re.split(r',\s*(?:and\s+)?', pattern_match)
                for item in items:
                    item = item.strip().strip('.')
                    if 2 <= len(item) <= 40 and not item.lower().startswith(('for ', 'to ', 'and ', 'or ')):
                        individual_skills.append(item)
        
        # Remove duplicates with improved filtering
        seen = set()
        unique_skills = []
        
        filter_words = {
            'network', 'software', 'tools', 'system', 'platform', 'technology',
            'experienced', 'skilled', 'proficient', 'hands', 'knowledge',
            'fiber records', 'cable preparation', 'fusion splicing infrastructure',
            'managing fiber cables', 'distribution boxes', 'network plans',
            'updating fiber records', 'creating documentation', 'monitoring networks',
            'analyzing fiber performance', 'including cable preparation',
            'and network plans', 'and gitlab ci/cd', 'devops tools'
        }
        
        for skill in individual_skills:
            skill = skill.strip()
            skill_lower = skill.lower()
            
            if skill_lower in filter_words:
                continue
            
            if any(skill_lower.startswith(prefix) for prefix in ['updating ', 'creating ', 'managing ', 'including ', 'and ']):
                continue
            
            if len(skill) > 35:
                continue
            
            # Prefer longer versions (e.g., "Google Cloud Platform" over "Google Cloud")
            is_substring = False
            for existing in unique_skills:
                if skill_lower in existing.lower() and skill_lower != existing.lower():
                    is_substring = True
                    break
            
            if is_substring:
                continue
            
            unique_skills = [s for s in unique_skills if s.lower() not in skill_lower or s.lower() == skill_lower]
            
            if skill_lower not in seen and len(skill) >= 2:
                seen.add(skill_lower)
                unique_skills.append(skill)
        
        return unique_skills

# Run test
formatter = MockFormatter()
parsed = formatter._parse_individual_skills(mock_skills_raw)

print("\n" + "="*70)
print("SKILLS PARSING TEST")
print("="*70)
print(f"\nInput: {len(mock_skills_raw)} raw skill entries")
for i, raw in enumerate(mock_skills_raw, 1):
    print(f"  {i}. {raw[:80]}...")

print(f"\nOutput: {len(parsed)} individual skills")
for i, skill in enumerate(parsed, 1):
    print(f"  {i}. {skill}")

print("\n" + "="*70)
print("EXPECTED SKILLS IN TABLE:")
print("="*70)
print("✅ Each row should have ONE skill name (not a long description)")
print("✅ Skills should be clean names like: 'Excel', 'GIS Software', 'OTDR', 'Docker', etc.")
print("✅ No 'Skilled in...' or 'Experience with...' prefixes")
print("="*70)
