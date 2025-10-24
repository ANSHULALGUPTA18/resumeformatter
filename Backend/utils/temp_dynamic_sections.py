    def _add_dynamic_candidate_sections(self, doc):
        """
        Dynamically detect and add any sections from candidate resume that don't exist in template.
        This handles custom sections like hobbies, volunteer work, publications, etc.
        Sections are added AFTER all template sections in template's formatting style.
        """
        added_count = 0
        
        # Get all section names from candidate resume
        candidate_sections = self.resume_data.get('sections', {})
        
        # Standard sections that we already handle
        standard_sections = {
            'summary', 'profile', 'objective', 'professional_summary',
            'employment', 'experience', 'work_history', 'work_experience', 'professional_experience',
            'education', 'academic_background', 'certificates', 'certifications',
            'skills', 'technical_skills', 'core_competencies'
        }
        
        # Find sections in candidate resume that aren't in template
        dynamic_sections = {}
        for section_name, section_content in candidate_sections.items():
            section_lower = section_name.lower().replace('_', ' ').replace('-', ' ')
            
            # Skip if it's a standard section we already processed
            if any(std in section_lower for std in standard_sections):
                continue
            
            # Skip if empty
            if not section_content or (isinstance(section_content, list) and len(section_content) == 0):
                continue
            
            # Check if this section already exists in template
            section_exists = False
            for template_section in self._existing_template_sections.values():
                if section_lower in template_section.lower() or template_section.lower() in section_lower:
                    section_exists = True
                    break
            
            if not section_exists:
                dynamic_sections[section_name] = section_content
                print(f"  🔍 Found dynamic section: {section_name} ({len(section_content) if isinstance(section_content, list) else 1} items)")
        
        if not dynamic_sections:
            return 0
        
        # Find insertion point: after last template section
        insertion_point = self._last_known_section_position + 10
        if insertion_point >= len(doc.paragraphs):
            insertion_point = len(doc.paragraphs) - 1
        
        print(f"  📍 Will insert dynamic sections after paragraph {insertion_point}")
        
        # Add each dynamic section
        for section_name, content in dynamic_sections.items():
            try:
                # Format section name
                display_name = section_name.replace('_', ' ').replace('-', ' ').title()
                
                # Insert section heading
                if insertion_point < len(doc.paragraphs):
                    anchor_para = doc.paragraphs[insertion_point]
                    heading_para = self._insert_paragraph_after(anchor_para, display_name.upper())
                else:
                    heading_para = doc.add_paragraph(display_name.upper())
                
                # Format heading
                for run in heading_para.runs:
                    run.bold = True
                    run.font.size = Pt(11)
                heading_para.paragraph_format.space_before = Pt(6)
                heading_para.paragraph_format.space_after = Pt(3)
                
                # Insert content
                last_para = heading_para
                content_list = content if isinstance(content, list) else [content]
                
                for item in content_list:
                    item_text = str(item).strip()
                    if item_text:
                        content_para = self._insert_paragraph_after(last_para, f"• {item_text}")
                        content_para.paragraph_format.left_indent = Inches(0.25)
                        for run in content_para.runs:
                            run.font.size = Pt(10)
                        content_para.paragraph_format.space_after = Pt(2)
                        last_para = content_para
                
                added_count += 1
                insertion_point += len(content_list) + 2
                print(f"  ✅ Added {display_name} section with {len(content_list)} items")
                
            except Exception as e:
                print(f"  ⚠️  Error adding {section_name}: {e}")
                continue
        
        return added_count
