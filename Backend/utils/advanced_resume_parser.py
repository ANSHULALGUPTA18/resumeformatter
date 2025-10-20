"""
Advanced Resume Parser
Extracts comprehensive information from resumes:
- Personal Details: Name, DOB, Email, Phone, Address, LinkedIn
- Experience: Company, Role, Duration, Responsibilities
- Education: Degree, Institution, Year, Grade
- Skills: Technical, Soft, Languages
- Projects, Certifications, Awards
"""

import pdfplumber
from docx import Document
import re
from datetime import datetime
from collections import defaultdict
import os

class ResumeParser:
    """Comprehensive resume parsing"""
    
    def __init__(self, file_path, file_type):
        self.file_path = file_path
        self.file_type = file_type
        self.raw_text = ""
        self.lines = []
        
    def parse(self):
        """Main parsing method"""
        print(f"\n{'='*70}")
        print(f"📋 PARSING RESUME: {self.file_path.split('/')[-1]}")
        print(f"{'='*70}\n")
        
        # Extract text
        if self.file_type == 'pdf':
            self.raw_text = self._extract_pdf_text()
        else:
            self.raw_text = self._extract_docx_text()
        
        self.lines = [line.strip() for line in self.raw_text.split('\n') if line.strip()]
        
        # Extract all information
        resume_data = {
            'name': self._extract_name(),
            'email': self._extract_email(),
            'phone': self._extract_phone(),
            'address': self._extract_address(),
            'linkedin': self._extract_linkedin(),
            'dob': self._extract_dob(),
            'summary': self._extract_summary(),
            'experience': self._extract_experience(),
            'education': self._extract_education(),
            'skills': self._extract_skills(),
            'projects': self._extract_projects(),
            'certifications': self._extract_certifications(),
            'awards': self._extract_awards(),
            'languages': self._extract_languages(),
            'sections': self._extract_sections(),
            'raw_text': self.raw_text
        }
        
        self._print_parsing_summary(resume_data)
        return resume_data
    
    def _extract_pdf_text(self):
        """Extract text from PDF"""
        try:
            with pdfplumber.open(self.file_path) as pdf:
                return '\n'.join([page.extract_text() or '' for page in pdf.pages])
        except Exception as e:
            print(f"❌ Error extracting PDF text: {e}")
            return ""
    
    def _extract_docx_text(self):
        """Extract text from DOCX (paragraphs, tables, headers/footers)"""
        try:
            doc = Document(self.file_path)
            texts = []

            # Main body paragraphs
            for para in doc.paragraphs:
                if para.text is not None:
                    texts.append(para.text)

            # Tables content
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for p in cell.paragraphs:
                            if p.text is not None:
                                texts.append(p.text)

            # Headers and footers
            try:
                for section in doc.sections:
                    for p in section.header.paragraphs:
                        if p.text is not None:
                            texts.append(p.text)
                    for p in section.footer.paragraphs:
                        if p.text is not None:
                            texts.append(p.text)
            except Exception:
                pass

            # Join and normalize lines
            return '\n'.join([t for t in texts if t and t.strip()])
        except Exception as e:
            print(f"❌ Error extracting DOCX text: {e}")
            return ""
    
    def _extract_name(self):
        """Extract candidate name robustly using context around contact lines"""
        lines = self.lines

        # Helper: find first line index that contains email or phone
        email_idx = phone_idx = None
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
        phone_patterns = [
            r'(?:\+?\d{1,3}[-\s]?)?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}',  # US formats
            r'(?:\+?91[-\s]?)?\d{10}',  # India +91XXXXXXXXXX or 10 digits
            r'\+?\d{1,3}[-\s]?\d{2,5}[-\s]?\d{5,10}',  # Intl generic
        ]
        phone_regexes = [re.compile(p) for p in phone_patterns]

        for idx, line in enumerate(lines[:30]):
            if email_idx is None and email_pattern.search(line):
                email_idx = idx
            if phone_idx is None and any(r.search(line) for r in phone_regexes):
                phone_idx = idx
            if email_idx is not None and phone_idx is not None:
                break

        # Try lines above the earliest contact line
        pivot = min([i for i in [email_idx, phone_idx] if i is not None], default=None)
        if pivot is not None:
            for i in range(max(0, pivot - 3), pivot + 1):
                line = lines[i].strip()
                if self._has_contact_info(line):
                    continue
                # Name heuristics: 2-4 words, mostly capitalized
                words = line.split()
                if 1 < len(words) <= 5 and sum(w[:1].isupper() for w in words) >= max(2, len(words) - 1):
                    return line

        # Fallback: scan first 10 non-contact lines for a likely name
        for line in lines[:10]:
            if self._has_contact_info(line):
                continue
            if len(line) < 3 or len(line) > 60:
                continue
            if re.match(r'^[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z\-\.]+){1,3}$', line.strip()):
                return line.strip()

        # Fallback 2: derive from file name
        try:
            base = os.path.basename(self.file_path)
            stem = os.path.splitext(base)[0]
            # Remove common words and separators
            tokens = re.split(r'[\W_]+', stem)
            blacklist = {"resume", "cv", "profile", "updated", "final", "copy", "doc", "docx", "pdf"}
            tokens = [t for t in tokens if t and t.lower() not in blacklist]
            if 1 <= len(tokens) <= 4:
                name_guess = ' '.join(tokens)
                # Capitalize words
                return ' '.join(w[:1].upper() + w[1:] for w in name_guess.split())
        except Exception:
            pass

        return "Unknown Candidate"
    
    def _extract_email(self):
        """Extract email address"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, self.raw_text)
        return match.group(0) if match else ""
    
    def _extract_phone(self):
        """Extract phone number (supports international formats)"""
        phone_patterns = [
            r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US formats
            r'(?:\+?91[-.\s]?)?\d{10}',  # India
            r'\+?\d{1,3}[-.\s]?\d{2,5}[-.\s]?\d{5,10}',  # Intl generic
        ]

        for pattern in phone_patterns:
            match = re.search(pattern, self.raw_text)
            if match:
                return match.group(0)
        return ""
    
    def _extract_address(self):
        """Extract address"""
        # Look for lines with address keywords
        address_keywords = ['street', 'avenue', 'road', 'city', 'state', 'zip', 'postal']
        for line in self.lines:
            if any(keyword in line.lower() for keyword in address_keywords):
                return line
        return ""
    
    def _extract_linkedin(self):
        """Extract LinkedIn profile"""
        linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+'
        match = re.search(linkedin_pattern, self.raw_text, re.IGNORECASE)
        return match.group(0) if match else ""
    
    def _extract_dob(self):
        """Extract date of birth"""
        dob_patterns = [
            r'(?:DOB|Date of Birth|Birth Date)[\s:]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(?:DOB|Date of Birth|Birth Date)[\s:]+(\w+ \d{1,2},? \d{4})',
        ]
        
        for pattern in dob_patterns:
            match = re.search(pattern, self.raw_text, re.IGNORECASE)
            if match:
                return match.group(1)
        return ""
    
    def _extract_summary(self):
        """Extract professional summary/objective - with or without explicit heading."""
        summary_keywords = ['summary', 'objective', 'profile', 'about', 'professional summary']
        
        # METHOD 1: Look for explicit summary section heading
        for i, line in enumerate(self.lines):
            if any(keyword in line.lower() for keyword in summary_keywords) and len(line) < 50:
                # Get next few lines as summary
                summary_lines = []
                for j in range(i+1, min(i+10, len(self.lines))):
                    if self._is_section_header(self.lines[j]):
                        break
                    if self.lines[j].strip():
                        summary_lines.append(self.lines[j])
                if summary_lines:
                    return ' '.join(summary_lines)
        
        # METHOD 2: Detect implicit summary - a descriptive paragraph before experience section
        # Find where the experience section starts
        exp_start = None
        exp_keywords = ['experience', 'work history', 'employment', 'professional experience', 'work experience', 'career history']
        for i, line in enumerate(self.lines):
            if any(kw in line.lower() for kw in exp_keywords) and len(line) < 50:
                exp_start = i
                break
        
        # Search lines after contact info but before experience section
        contact_end = 0
        for i, line in enumerate(self.lines[:20]):
            if self._has_contact_info(line):
                contact_end = i + 1
        
        # Look for summary-like paragraphs in the header area (after contact, before experience)
        search_start = contact_end
        search_end = exp_start if exp_start else 20
        
        for i in range(search_start, min(search_end, len(self.lines))):
            line = self.lines[i].strip()
            
            # Skip section headers, very short lines, and contact info
            if self._is_section_header(line) or len(line) < 80 or self._has_contact_info(line):
                continue
            
            # Check if this looks like summary text
            if self._looks_like_summary_text(line):
                # Accumulate multi-line summary
                summary_lines = [line]
                j = i + 1
                while j < min(i + 8, len(self.lines)):
                    next_line = self.lines[j].strip()
                    # Stop at section headers or if we hit experience/education
                    if self._is_section_header(next_line):
                        break
                    # Continue if it looks like part of the summary
                    if next_line and len(next_line) > 40 and not self._has_contact_info(next_line):
                        summary_lines.append(next_line)
                    j += 1
                
                result = ' '.join(summary_lines)
                if len(result) > 100:  # Ensure it's substantial enough
                    return result
        
        return ""
    
    def _extract_experience(self):
        """Extract work experience details with robust pairing (dates + role/company)."""
        experiences = []
        
        # CRITICAL: Search ENTIRE document for employment entries, not just experience section
        # This handles resumes where education/skills sections appear in the middle of employment
        section = self._find_section(['experience', 'work history', 'employment', 'professional experience', 'work experience', 'career history'])
        
        if not section:
            print("  ⚠️  No experience section found, searching entire document")
            # Fallback: use all lines
            section = self.lines
        else:
            print(f"  📋 Found experience section with {len(section)} lines")
            # ENHANCEMENT: Also scan lines AFTER the experience section for additional jobs
            # (in case education section interrupted the employment section)
            # BUT: Stop at SKILLS or final EDUCATION section to avoid mixing content
            exp_section_end = -1
            for idx, line in enumerate(self.lines):
                if any(keyword in line.lower() for keyword in ['experience', 'work history', 'employment']):
                    exp_section_end = idx
                    break
            
            if exp_section_end > 0:
                # Add remaining lines but STOP at SKILLS/EDUCATION sections
                remaining_lines = []
                for idx in range(exp_section_end + len(section) + 1, len(self.lines)):
                    line = self.lines[idx]
                    line_lower = line.lower().strip()
                    
                    # Stop if we hit SKILLS or EDUCATION section (these are separate)
                    if any(kw in line_lower for kw in ['skills', 'education', 'certifications', 'projects']) and len(line) < 50:
                        print(f"  🛑 Stopped extended search at: '{line[:40]}'")
                        break
                    
                    remaining_lines.append(line)
                
                if remaining_lines:
                    section.extend(remaining_lines)
                    print(f"  📋 Extended search to include {len(remaining_lines)} additional lines")

        # Normalize lines and strip bullets
        lines = [self._strip_bullet(self._normalize_text(l)) for l in section if l and l.strip()]
        
        print(f"  📝 First 10 lines of experience section:")
        for idx, l in enumerate(lines[:10]):
            print(f"     {idx}: {l[:80]}")
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Skip very short or empty lines
            if len(line) < 3:
                i += 1
                continue

            # Case A: Line with dates - intelligently detect company/role/dates in any format
            if self._contains_date_range(line):
                duration = self._clean_years(line)
                
                # Extract text by removing dates from current line
                text_without_dates = self._extract_role_from_dated_line(line)
                
                company = ''
                role = ''
                
                # Strategy: Check previous line, current line, and next line to find company and role
                
                # Check PREVIOUS line (might be company)
                prev_line = ''
                if i > 0 and not self._is_section_header(lines[i-1]) and not self._contains_date_range(lines[i-1]) and not self._looks_like_detail_bullet(lines[i-1]):
                    prev_line = lines[i-1].strip()
                
                # Check NEXT line (might be role or company)
                next_line = ''
                j = i + 1
                while j < len(lines) and len(lines[j].strip()) < 3:
                    j += 1
                if j < len(lines) and not self._is_section_header(lines[j]) and not self._contains_date_range(lines[j]):
                    next_line = lines[j].strip()
                
                # DECISION LOGIC: Determine what each line contains
                
                # If current line has location markers (-, ,), it's likely company+location
                has_location = any(marker in text_without_dates for marker in [' - ', ', ', ' – ', ' — '])
                
                # If current line has role keywords, it might be role
                has_role_keyword = any(kw in text_without_dates.lower() for kw in ['manager', 'coordinator', 'director', 'specialist', 'analyst', 'engineer', 'developer', 'consultant', 'officer', 'assistant', 'supervisor', 'accountant', 'administrator'])
                
                if has_location and not has_role_keyword:
                    # Current line: Company+Location+Dates
                    # Next line: Role
                    company = self._strip_location(text_without_dates).strip()
                    role = next_line
                    print(f"    📌 Format: Company+Location+Dates | Role on next line")
                    print(f"       Company: '{company}' | Role: '{role}'")
                    
                elif has_location and has_role_keyword:
                    # Current line might have: Company+Location+Role+Dates (all in one)
                    # Try to split by role keyword
                    parts = text_without_dates.split()
                    # Simple heuristic: everything before role keyword is company
                    for idx, word in enumerate(parts):
                        if any(kw in word.lower() for kw in ['manager', 'coordinator', 'director', 'specialist', 'analyst', 'engineer', 'developer', 'consultant', 'officer', 'assistant', 'supervisor', 'accountant']):
                            company = ' '.join(parts[:idx]).strip()
                            role = ' '.join(parts[idx:]).strip()
                            break
                    
                    if not company:
                        # Fallback: strip location and use as company
                        company = self._strip_location(text_without_dates).strip()
                        role = next_line if next_line else text_without_dates
                    
                    print(f"    📌 Format: Company+Location+Role+Dates (combined)")
                    print(f"       Company: '{company}' | Role: '{role}'")
                    
                elif prev_line:
                    # Previous line: Company+Location
                    # Current line: Role+Dates
                    company = self._strip_location(prev_line).strip()
                    role = text_without_dates.strip()
                    print(f"    📌 Format: Company on previous | Role+Dates on current")
                    print(f"       Company: '{company}' | Role: '{role}'")
                    
                else:
                    # Fallback: Current line is role+dates, look for company elsewhere
                    role = text_without_dates.strip()
                    if next_line:
                        company = self._strip_location(next_line).strip()
                        print(f"    📌 Format: Role+Dates on current | Company on next")
                    else:
                        company = ''
                        print(f"    📌 Format: Role+Dates only (no company found)")
                    print(f"       Company: '{company}' | Role: '{role}'")
                
                role = role.strip()
                company = company.strip()

                exp = {
                    'company': company,
                    'role': role,
                    'title': f"{role} - {company}",
                    'duration': duration,
                    'details': []
                }

                # Collect following detail bullets until next date or header
                k = i + 1
                while k < len(lines):
                    # CRITICAL FIX: Only break if it's a NEW job entry (not just a detail with dates)
                    # A new job entry has dates AND looks like a role/company line (short, title case)
                    # A detail bullet with dates is long and starts with action verb
                    if self._is_section_header(lines[k]):
                        break
                    
                    # Check if this is a new job entry (has dates AND looks like header, not detail)
                    if self._contains_date_range(lines[k]):
                        # CRITICAL: Check if this looks like a job entry (company + role + dates)
                        # Job entries have: location markers, title case words, or role keywords
                        line_k = lines[k]
                        has_location = any(marker in line_k for marker in [' - ', ', ', ' – ', '-'])
                        has_role_keywords = any(kw in line_k.lower() for kw in ['manager', 'coordinator', 'director', 'specialist', 'analyst', 'engineer', 'developer', 'consultant', 'officer', 'assistant', 'supervisor'])
                        
                        # If it has location markers or role keywords, it's likely a job entry
                        if has_location or has_role_keywords:
                            print(f"    🔄 Found new job entry while collecting details: '{line_k[:60]}'")
                            # It's a new job entry, stop collecting details
                            break
                        
                        # If it looks like a detail bullet, keep it as detail
                        if self._looks_like_detail_bullet(line_k):
                            detail = line_k.strip()
                            if detail and len(detail) > 10:
                                exp['details'].append(detail)
                            k += 1
                            continue
                        else:
                            # It's a new job entry, stop collecting details
                            break
                    
                    detail = self._strip_bullet(lines[k]).strip()
                    # Merge tiny fragments like "Word", "Access)" or "reporting"
                    if exp['details'] and self._should_merge_fragment(exp['details'][-1], detail):
                        exp['details'][-1] = self._merge_fragment(exp['details'][-1], detail)
                        k += 1
                        continue
                    # Skip very short lines and lines that look like section summaries
                    if detail and len(detail) > 10 and not self._looks_like_summary_text(detail):
                        exp['details'].append(detail)
                    k += 1
                
                experiences.append(exp)
                print(f"    ✓ Entry {len(experiences)}: {company or '(no company)'} - {role or '(no role)'} ({duration}) [{len(exp['details'])} details]")
                i = k
                continue

            # Case B: Role/company line followed by date line
            if self._looks_like_company_or_role(line):
                company, role = self._parse_company_role_line(line)
                company, role = self._strip_location(company), self._strip_location(role)
                # Look ahead for date
                j = i + 1
                duration = ''
                if j < len(lines) and self._contains_date_range(lines[j]):
                    duration = self._clean_years(lines[j])
                    j += 1
                exp = {
                    'company': company,
                    'role': role,
                    'title': line,
                    'duration': duration,
                    'details': []
                }
                # Collect details
                k = j
                while k < len(lines):
                    if self._contains_date_range(lines[k]) or self._looks_like_company_or_role(lines[k]) or self._is_section_header(lines[k]):
                        break
                    detail = self._strip_bullet(lines[k]).strip()
                    if exp['details'] and self._should_merge_fragment(exp['details'][-1], detail):
                        exp['details'][-1] = self._merge_fragment(exp['details'][-1], detail)
                        k += 1
                        continue
                    # Skip lines that look like summary text
                    if detail and not self._looks_like_summary_text(detail):
                        exp['details'].append(detail)
                    k += 1
                experiences.append(exp)
                print(f"    ✓ Parsed experience: {company} - {role} ({duration})")
                i = k
                continue

            i += 1
        
        print(f"  ✅ Total experiences extracted: {len(experiences)}")
        return experiences
    
    def _parse_company_role_line(self, line):
        """Parse a line to extract company and role"""
        # Common patterns:
        # "Company Name - Role Title"
        # "Role Title at Company Name"
        # "Company Name, Role Title"
        # "Role Title | Company Name"
        
        if ' - ' in line or ' – ' in line:
            # Split by dash
            parts = re.split(r'\s+[-–]\s+', line, maxsplit=1)
            if len(parts) == 2:
                # Usually "Company - Role" or "Role - Company"
                # Heuristic: if first part has common company indicators, it's company
                if any(word in parts[0].lower() for word in ['inc', 'corp', 'ltd', 'llc', 'company', 'technologies', 'systems']):
                    return parts[0].strip(), parts[1].strip()
                else:
                    # Assume first is role, second is company
                    return parts[1].strip(), parts[0].strip()
        
        elif ' at ' in line.lower():
            # "Role at Company"
            parts = re.split(r'\s+at\s+', line, flags=re.IGNORECASE, maxsplit=1)
            if len(parts) == 2:
                return parts[1].strip(), parts[0].strip()
        
        elif '|' in line:
            # "Role | Company"
            parts = line.split('|', maxsplit=1)
            if len(parts) == 2:
                return parts[1].strip(), parts[0].strip()
        
        elif ',' in line:
            # "Company, Role" or "Role, Company"
            parts = line.split(',', maxsplit=1)
            if len(parts) == 2:
                # Heuristic: if first part has company indicators
                if any(word in parts[0].lower() for word in ['inc', 'corp', 'ltd', 'llc', 'company', 'technologies', 'systems']):
                    return parts[0].strip(), parts[1].strip()
                else:
                    return parts[1].strip(), parts[0].strip()
        
        # If no pattern matched, assume entire line is company or role
        # Check if it looks more like a company name
        if any(word in line.lower() for word in ['inc', 'corp', 'ltd', 'llc', 'company', 'technologies', 'systems', 'solutions']):
            return line.strip(), ''
        else:
            # Assume it's a role
            return '', line.strip()
        
        return line.strip(), ''
    
    def _extract_education(self):
        """Extract education - combine degree + institution properly.
        Enhanced to detect High School and similar qualifications and to clean degree text.
        """
        education = []
        section = self._find_section(['education', 'academic', 'qualification', 'academics'])
        if not section:
            print("  ⚠️  No education section found; attempting global scan")
            # Global scan fallback across entire resume lines
            education = self._extract_education_global()
            print(f"  ✅ Global scan produced {len(education)} education entries")
            return education
        
        print(f"  🎓 Found education section with {len(section)} lines")
        
        # Filter out lines that clearly look like work experience (have company/role patterns)
        filtered_section = []
        for line in section:
            line_lower = line.lower()
            
            # Skip lines that look like job titles or company names with employment indicators
            if any(word in line_lower for word in ['coordinator', 'manager', 'director', 'assistant', 'specialist', 'analyst']):
                if not any(edu_word in line_lower for edu_word in ['university', 'college', 'school', 'degree', 'bachelor', 'master']):
                    print(f"    ⚠️  Skipping potential experience line in education: {line[:60]}")
                    continue
            
            # Skip lines that are clearly experience bullets (start with action verbs typical of work)
            line_stripped = line.strip().lstrip('•–—-*● ')
            first_word = line_stripped.split()[0].lower() if line_stripped.split() else ''
            
            work_action_verbs = [
                'managed', 'oversaw', 'coordinated', 'conducted', 'led', 'supervised',
                'maintained', 'provided', 'facilitated', 'assisted', 'processed',
                'tracked', 'monitored', 'collaborated', 'acted', 'demonstrated',
                'proficient', 'applied', 'experienced', 'tested', 'collected'
            ]
            
            # If line starts with work action verb and doesn't contain education keywords, skip it
            if first_word in work_action_verbs:
                if not any(edu_word in line_lower for edu_word in ['university', 'college', 'school', 'degree', 'bachelor', 'master', 'graduation', 'gpa', 'graduated']):
                    print(f"    ⚠️  Skipping work-related bullet in education: {line[:60]}")
                    continue
            
            filtered_section.append(line)
        
        section = filtered_section
        print(f"  🎓 After filtering: {len(section)} lines")

        lines = [self._normalize_text(l) for l in section if l and l.strip()]
        i = 0
        while i < len(lines):
            line = self._strip_bullet(lines[i])
            
            # Skip empty or very short lines
            if len(line) < 5:
                i += 1
                continue

            # Check if this line contains degree keywords
            degree_keywords = [
                'bachelor', 'master', 'phd', 'mba', 'bsc', 'msc', 'b.sc', 'm.sc', 'degree', 'diploma',
                'high school', 'secondary school', 'higher secondary', 'matriculation', 'ssc', 'hsc', 'ged'
            ]
            has_degree = any(kw in line.lower() for kw in degree_keywords)
            has_institution = any(k in line.lower() for k in ['university', 'college', 'school', 'institute', 'academy'])
            
            # Only process if it looks like a degree line
            if has_degree or (has_institution and ':' in line):
                degree, institution = self._parse_degree_institution_line(line)
                year = self._clean_years(line)

                # Clean year tokens and generic suffixes from degree text
                if degree:
                    degree = re.sub(r'\b(?:19|20)\d{2}\b', '', degree)
                    degree = re.sub(r'\b(class of|graduation|graduated|passed out)\b', '', degree, flags=re.IGNORECASE)
                    degree = re.sub(r'\s+', ' ', degree).strip(' ,.;:-')
                
                # If institution is empty, check next line
                if not institution and i + 1 < len(lines):
                    next_line = self._strip_bullet(lines[i + 1])
                    if any(k in next_line.lower() for k in ['university', 'college', 'school', 'institute', 'academy']):
                        institution = self._strip_location(next_line).strip()
                        # Also get year from next line if not already found
                        if not year:
                            year = self._clean_years(next_line)
                        i += 1  # Skip the institution line
                
                # Collect details (but skip lines that look like other education entries or work experience)
                details = []
                j = i + 1
                while j < len(lines) and j < i + 4:
                    detail_line = self._strip_bullet(lines[j])
                    # Stop if we hit another degree entry
                    if any(kw in detail_line.lower() for kw in degree_keywords):
                        break
                    if self._is_section_header(detail_line):
                        break
                    
                    # Skip lines that start with work action verbs (these are work experience, not education)
                    detail_stripped = detail_line.strip().lstrip('•–—-*● ')
                    first_word_detail = detail_stripped.split()[0].lower() if detail_stripped.split() else ''
                    if first_word_detail in ['managed', 'oversaw', 'coordinated', 'conducted', 'maintained', 'provided', 'facilitated']:
                        print(f"      ⚠️  Skipping work bullet in education details: {detail_line[:50]}")
                        j += 1
                        continue
                    
                    # Add as detail if substantial and not an institution-only line
                    is_institution_only = any(k in detail_line.lower() for k in ['university', 'college', 'school']) and len(detail_line.split()) < 6
                    if len(detail_line) > 15 and not is_institution_only:
                        details.append(detail_line)
                    j += 1
                
                # Only add if we have at least a degree or institution AND they look like education content
                # Skip if degree/institution contain work-related terms
                degree_looks_valid = degree and not any(word in degree.lower() for word in ['coordinator', 'managed', 'oversaw', 'conducted', 'maintained'])
                institution_looks_valid = institution or degree_looks_valid  # Institution can be empty if degree is valid
                
                if (degree or institution) and (degree_looks_valid or institution):
                    edu = {
                        'degree': degree.strip(),
                        'institution': institution.strip(),
                        'year': year,
                        'details': details
                    }
                    education.append(edu)
                    print(f"    ✓ Parsed edu: {degree or '(no degree)'} - {institution or '(no inst)'} ({year})")
                else:
                    print(f"    ⚠️  Skipped invalid education entry: degree='{degree[:40] if degree else ''}'")
                
                i = j
                continue

            i += 1
        
        print(f"  ✅ Total education entries extracted: {len(education)}")
        return education

    def _extract_education_global(self):
        """Fallback: scan all lines for education-like entries even if no explicit section header exists."""
        results = []
        seen = set()
        degree_keywords = [
            'bachelor', 'master', 'phd', 'mba', 'bsc', 'msc', 'b.sc', 'm.sc', 'degree', 'diploma',
            'high school', 'secondary school', 'higher secondary', 'matriculation', 'ssc', 'hsc', 'ged'
        ]
        institution_keywords = ['university', 'college', 'school', 'institute', 'academy']
        work_terms = ['coordinator', 'manager', 'director', 'assistant', 'specialist', 'analyst']

        for idx, raw in enumerate(self.lines):
            line = self._normalize_text(raw)
            if not line or len(line) < 5 or self._is_section_header(line):
                continue
            low = line.lower()
            # Skip obvious work lines
            if any(w in low for w in work_terms) and not any(k in low for k in institution_keywords + degree_keywords):
                continue
            if any(k in low for k in degree_keywords + institution_keywords):
                degree, institution = self._parse_degree_institution_line(line)
                year = self._clean_years(line)
                degree = re.sub(r'\b(?:19|20)\d{2}\b', '', degree or '').strip(' ,.;:-')
                if not (degree or institution):
                    continue
                key = (degree.lower(), institution.lower(), year)
                if key in seen:
                    continue
                seen.add(key)
                results.append({'degree': degree, 'institution': institution, 'year': year, 'details': []})

                # Also peek at the next line if it likely contains the institution/year
                if not institution and idx + 1 < len(self.lines):
                    nxt = self._normalize_text(self.lines[idx + 1])
                    if any(k in nxt.lower() for k in institution_keywords):
                        inst2 = self._strip_location(nxt)
                        results[-1]['institution'] = inst2
                        if not results[-1]['year']:
                            results[-1]['year'] = self._clean_years(nxt)

        # Prefer most recent entries: sort by year descending when available
        def year_key(e):
            y = e.get('year') or ''
            m = re.search(r'((?:19|20)\d{2})$', y)
            return int(m.group(1)) if m else -1
        results.sort(key=year_key, reverse=True)
        # Limit to 5
        return results[:5]

    # ---------------------- Helpers ----------------------
    def _normalize_text(self, s):
        # Remove odd unicode like 'ï¼' and zero-width, collapse spaces
        if not s:
            return ''
        # Remove zero-width and BOM characters
        s = s.replace('\u200b', ' ').replace('\ufeff', ' ')
        # Remove common garbage unicode
        s = s.replace('ï¼', ' ').replace('â€"', '-').replace('–', '-').replace('—', '-')
        # Normalize quotes and apostrophes
        s = s.replace(''', "'").replace(''', "'").replace('"', '"').replace('"', '"')
        # Collapse multiple spaces
        s = re.sub(r'\s+', ' ', s).strip()
        return s

    def _strip_location(self, s):
        if not s:
            return s
        # Remove trailing city/state fragments after comma
        s = re.sub(r',[^,]*\b(?:city|state|india|usa|uk)\b.*$', '', s, flags=re.IGNORECASE)
        return s.strip()

    def _clean_years(self, s):
        """Normalize date ranges.
        Prefer 'Mon YYYY-Mon YYYY' if months present; else 'YYYY-YYYY' or 'YYYY'.
        """
        if not s:
            return ''
        s = self._normalize_text(s)
        s = re.sub(r'[–—]', '-', s)
        s = re.sub(r'\s*(to|–|—|-)\s*', '-', s, flags=re.IGNORECASE)

        present = bool(re.search(r'\b(current|present)\b', s, re.IGNORECASE))

        month_map = {
            'january': 'Jan', 'jan': 'Jan',
            'february': 'Feb', 'feb': 'Feb',
            'march': 'Mar', 'mar': 'Mar',
            'april': 'Apr', 'apr': 'Apr',
            'may': 'May',
            'june': 'Jun', 'jun': 'Jun',
            'july': 'Jul', 'jul': 'Jul',
            'august': 'Aug', 'aug': 'Aug',
            'september': 'Sept', 'sept': 'Sept', 'sep': 'Sept',
            'october': 'Oct', 'oct': 'Oct',
            'november': 'Nov', 'nov': 'Nov',
            'december': 'Dec', 'dec': 'Dec',
        }
        def abbr(m):
            return month_map.get(m.lower(), m[:3].title())

        my = [m.groups() for m in re.finditer(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s*(?:,\s*)?((?:19|20)\d{2})\b', s, flags=re.IGNORECASE)]
        if my:
            sm, sy = my[0]
            sm = abbr(sm)
            if len(my) >= 2:
                em, ey = my[-1]
                em = abbr(em)
                return f"{sm} {sy}-{em} {ey}"
            if present:
                return f"{sm} {sy}-Present"
            yrs = re.findall(r'\b((?:19|20)\d{2})\b', s)
            if len(yrs) >= 2:
                return f"{sm} {yrs[0]}-{yrs[-1]}"
            return f"{sm} {sy}"

        years = re.findall(r'\b(?:19|20)\d{2}\b', s)
        if len(years) >= 2:
            return f"{years[0]}-{years[-1]}"
        elif len(years) == 1:
            return years[0]
        return ''
    
    def _parse_degree_institution_line(self, line):
        """Parse a line to extract degree and institution"""
        # Common patterns:
        # "Bachelor of Science, MIT"
        # "Master's in Computer Science - Stanford University"
        # "MBA | Harvard Business School"
        s = self._normalize_text(line)
        s = self._strip_bullet(s)
        # Prefer splitting at an institution keyword boundary
        m = re.search(r'(university|college|school|institute|academy)\b.*', s, flags=re.IGNORECASE)
        if m:
            degree = s[:m.start()].strip(' ,;:-')
            institution = s[m.start():].strip()
            # Remove trailing location fragments
            institution = self._strip_location(institution)
            return degree, institution
        
        if ',' in s:
            parts = s.split(',', maxsplit=1)
            return parts[0].strip(), parts[1].strip()
        
        elif ' - ' in s or ' – ' in s:
            parts = re.split(r'\s+[-–]\s+', s, maxsplit=1)
            if len(parts) == 2:
                return parts[0].strip(), parts[1].strip()
        
        elif '|' in s:
            parts = s.split('|', maxsplit=1)
            if len(parts) == 2:
                return parts[0].strip(), parts[1].strip()
        
        elif ' from ' in s.lower():
            parts = re.split(r'\s+from\s+', s, flags=re.IGNORECASE, maxsplit=1)
            if len(parts) == 2:
                return parts[0].strip(), parts[1].strip()
        
        # If no pattern, return entire line as degree
        return s.strip(), ''

    def _strip_bullet(self, s):
        if not s:
            return s
        return re.sub(r'^[\s•\-–—*●]+', '', s)

    def _extract_role_from_dated_line(self, s):
        """Remove date expressions from a dated line to recover the job title/role text."""
        if not s:
            return ''
        t = self._strip_bullet(self._normalize_text(s))
        # Remove month names + year e.g., 'Aug 2007', 'July 2025'
        t = re.sub(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-zA-Z]*\s+(?:19|20)\d{2}\b', '', t, flags=re.IGNORECASE)
        # Remove standalone years and connectors
        t = re.sub(r'\b(?:19|20)\d{2}\b', '', t)
        t = re.sub(r'\b(to|–|—|-)\b', '', t, flags=re.IGNORECASE)
        t = re.sub(r'\b(current|present)\b', '', t, flags=re.IGNORECASE)
        # Collapse spaces and trim
        t = re.sub(r'\s+', ' ', t).strip(' ,;:- ')
        return t
    
    def _extract_skills(self):
        """Extract skills - preserve all content from SKILLS section as-is.
        Each bullet/line is treated as one skill entry. We avoid splitting on '•' or commas
        to prevent breaking phrases like "Microsoft Office Suite (Excel, Word, Access)".
        Also stitch short continuation lines to the previous bullet when needed.
        """
        skills = []
        skills_section = self._find_section(['skills', 'technical skills', 'competencies', 'expertise'])
        
        if skills_section:
            buf = ''
            for raw in skills_section:
                t = self._strip_bullet(self._normalize_text(raw))
                if not t or self._is_section_header(t):
                    continue
                
                # ONLY filter: lines with full date ranges (definitely experience entries)
                if self._contains_date_range(t):
                    print(f"    ⏭️  Skipping dated line in skills: {t[:60]}")
                    continue
                
                # ONLY filter: extremely long paragraphs (>300 chars - clearly not a skill line)
                if len(t) > 300:
                    print(f"    ⏭️  Skipping paragraph in skills: {t[:60]}...")
                    continue
                
                # Continuation line heuristic: very short fragment, likely part of previous line
                if buf and self._should_merge_fragment(buf, t):
                    buf = self._merge_fragment(buf, t)
                    continue
                # Flush previous buffer
                if buf:
                    skills.append(buf)
                    buf = ''
                buf = t
            if buf:
                skills.append(buf)
        
        # Debug output: show extracted skills
        if skills:
            print(f"  🛠️  Extracted {len(skills)} skills:")
            for idx, skill in enumerate(skills[:10]):
                print(f"     {idx+1}. {skill[:80]}")
            if len(skills) > 10:
                print(f"     ... and {len(skills) - 10} more")
        
        return skills
    
    def _extract_projects(self):
        """Extract projects"""
        projects = []
        projects_section = self._find_section(['projects', 'key projects', 'project work'])
        
        if projects_section:
            current_project = {}
            for line in projects_section:
                if line and not line.startswith('•') and not self._is_section_header(line):
                    if current_project:
                        projects.append(current_project)
                    current_project = {'name': line, 'details': []}
                elif line:
                    current_project.setdefault('details', []).append(line)
            
            if current_project:
                projects.append(current_project)
        
        return projects
    
    def _extract_certifications(self):
        """Extract certifications"""
        certifications = []
        cert_section = self._find_section(['certifications', 'certificates', 'licenses'])
        
        if cert_section:
            for line in cert_section:
                if line and not self._is_section_header(line):
                    certifications.append(line)
        
        return certifications
    
    def _extract_awards(self):
        """Extract awards and achievements"""
        awards = []
        awards_section = self._find_section(['awards', 'achievements', 'honors', 'recognition'])
        
        if awards_section:
            for line in awards_section:
                if line and not self._is_section_header(line):
                    awards.append(line)
        
        return awards
    
    def _extract_languages(self):
        """Extract languages"""
        languages = []
        lang_section = self._find_section(['languages', 'language proficiency'])
        
        if lang_section:
            for line in lang_section:
                if line and not self._is_section_header(line):
                    languages.append(line)
        
        return languages
    
    def _extract_sections(self):
        """Extract all sections for flexible formatting"""
        sections = defaultdict(list)
        current_section = None
        
        for line in self.lines:
            if self._is_section_header(line):
                current_section = line.lower().strip()
            elif current_section and line:
                sections[current_section].append(line)
        
        return dict(sections)
    
    def _find_section(self, keywords):
        """Find section by keywords - with improved boundary detection"""
        section_lines = []
        in_section = False
        section_start_idx = -1
        
        # First pass: find the section start
        for idx, line in enumerate(self.lines):
            if any(keyword in line.lower() for keyword in keywords):
                in_section = True
                section_start_idx = idx
                break
        
        if not in_section:
            return section_lines
        
        # Second pass: collect lines until next section header
        for idx in range(section_start_idx + 1, len(self.lines)):
            line = self.lines[idx]
            
            # Stop at next section header
            if self._is_section_header(line):
                print(f"    🛑 Stopped at next section: '{line[:40]}'")
                break
            
            section_lines.append(line)
        
        return section_lines
    
    def _is_section_header(self, line):
        """Check if line is a section header"""
        if len(line) > 50:
            return False
        
        section_keywords = [
            'experience', 'education', 'skills', 'summary', 'objective',
            'projects', 'certifications', 'awards', 'languages', 'profile',
            'work history', 'employment', 'qualifications', 'achievements',
            'work experience', 'professional experience', 'career history'
        ]
        
        line_lower = line.lower().strip()
        return any(keyword == line_lower or line_lower.startswith(keyword) for keyword in section_keywords)
    
    def _looks_like_summary_text(self, text):
        """Check if text looks like summary/objective content rather than experience details"""
        if not text:
            return False
        
        # Summary text characteristics:
        # - Often starts with personal pronouns or adjectives
        # - Contains general career statements
        # - No action verbs typical of bullet points
        
        text_lower = text.lower().strip()
        
        # Skip if starts with typical summary phrases
        summary_starters = [
            'detail-oriented', 'results-oriented', 'highly motivated',
            'experienced professional', 'proven track record', 'dedicated',
            'proficient in', 'recognized for', 'skilled in',
            'strong background', 'extensive experience', 'adept at'
        ]
        
        # Check if line starts with these phrases (more likely to be summary)
        for starter in summary_starters:
            if text_lower.startswith(starter):
                return True
        
        # If the line is very long (>150 chars) and doesn't start with action verb, might be summary
        if len(text) > 150:
            action_verbs = ['managed', 'developed', 'created', 'led', 'coordinated', 
                          'implemented', 'executed', 'analyzed', 'designed', 'built',
                          'oversaw', 'directed', 'supervised', 'maintained', 'conducted',
                          'established', 'improved', 'increased', 'reduced', 'achieved',
                          'tracked', 'monitored', 'facilitated', 'collaborated', 'assisted',
                          'provided', 'processed', 'scheduled', 'organized']
            
            # Check if starts with action verb
            first_word = text_lower.split()[0] if text_lower.split() else ''
            if first_word not in action_verbs:
                return True
        
        return False
    
    def _has_contact_info(self, text):
        """Check if text contains contact information"""
        return bool(re.search(r'@|http|linkedin|\d{3}[-.\s]\d{3}', text, re.IGNORECASE))
    
    def _looks_like_company_or_role(self, line):
        """Check if line looks like company name or job title"""
        # Usually title case, not too long, no bullets
        return (line.istitle() or line.isupper()) and len(line) < 100 and not line.startswith('•')
    
    def _looks_like_detail_bullet(self, text):
        """Check if text looks like a detail bullet (starts with action verb or is descriptive)"""
        if not text:
            return False
        
        text_lower = text.lower().strip()
        
        # Common action verbs used in resume bullets
        action_verbs = [
            'managed', 'developed', 'created', 'led', 'coordinated', 
            'implemented', 'executed', 'analyzed', 'designed', 'built',
            'oversaw', 'directed', 'supervised', 'maintained', 'conducted',
            'established', 'improved', 'increased', 'reduced', 'achieved',
            'tracked', 'monitored', 'facilitated', 'collaborated', 'assisted',
            'provided', 'processed', 'scheduled', 'organized', 'acted',
            'demonstrated', 'tested', 'collected', 'ensured', 'handled',
            'performed', 'supported', 'delivered', 'prepared', 'reviewed',
            'updated', 'resolved', 'trained', 'documented', 'communicated',
            'participated', 'contributed', 'streamlined', 'optimized'
        ]
        
        # Check if starts with action verb
        first_word = text_lower.split()[0] if text_lower.split() else ''
        if first_word in action_verbs:
            return True
        
        # Check if line is long and descriptive (likely a detail)
        # Detail bullets are usually longer than company/role names
        if len(text) > 60 and not (text.istitle() or text.isupper()):
            return True
        
        return False
    
    def _contains_date_range(self, line):
        """Check if line contains date range"""
        date_patterns = [
            r'\b(19|20)\d{2}\b.*\b(19|20)\d{2}\b',  # 2020 - 2023
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4}',  # Jan 2020
            r'\d{1,2}/\d{4}',  # 01/2020
        ]
        return any(re.search(pattern, line, re.IGNORECASE) for pattern in date_patterns)

    def _should_merge_fragment(self, prev, curr):
        """Heuristic to decide if 'curr' is a continuation of 'prev' (fragment stitching).
        Merges tiny lines like 'Word', 'Access) and other', 'reporting', 'and documentation.' into the previous bullet.
        """
        if not curr:
            return False
        # Do not merge if curr looks like a section header or explicit new sentence with leading verb
        if self._is_section_header(curr) or self._looks_like_detail_bullet(curr):
            return False
        # Merge if curr is a very short fragment (<= 25 chars or <= 5 words)
        words = curr.split()
        if len(curr) <= 25 or len(words) <= 5:
            return True
        # Merge if previous line has open parenthesis not yet closed
        if prev and prev.count('(') > prev.count(')'):
            return True
        return False

    def _merge_fragment(self, prev, curr):
        """Join fragment 'curr' to 'prev' with an appropriate delimiter."""
        if not prev:
            return curr
        # If prev has an open parenthesis, separate with comma unless prev already ends with a space or comma
        if prev.count('(') > prev.count(')'):
            sep = ', ' if not prev.endswith((' ', ',')) else ''
            return (prev + sep + curr).strip()
        # If prev ends without terminal punctuation, add space
        if not prev.endswith(('.', '!', '?', ')', ']')):
            return (prev + ' ' + curr).strip()
        # Default: space join
        return (prev + ' ' + curr).strip()
    
    def _print_parsing_summary(self, data):
        """Print parsing summary"""
        print(f"👤 Name: {data['name']}")
        print(f"📧 Email: {data['email']}")
        print(f"📱 Phone: {data['phone']}")
        print(f"🔗 LinkedIn: {data['linkedin'][:50] if data['linkedin'] else 'Not found'}")
        print(f"📅 DOB: {data['dob']}")
        print(f"💼 Experience Entries: {len(data['experience'])}")
        print(f"🎓 Education Entries: {len(data['education'])}")
        print(f"🛠️  Skills: {len(data['skills'])}")
        print(f"📂 Projects: {len(data['projects'])}")
        print(f"🏆 Certifications: {len(data['certifications'])}")
        print(f"🏅 Awards: {len(data['awards'])}")
        print(f"🌐 Languages: {len(data['languages'])}")
        print(f"\n{'='*70}\n")


def parse_resume(file_path, file_type):
    """Main function to parse resume"""
    parser = ResumeParser(file_path, file_type)
    return parser.parse()
