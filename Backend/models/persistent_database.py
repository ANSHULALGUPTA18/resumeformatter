"""
Persistent Database using Azure Blob Storage
Replaces local SQLite with cloud-persistent storage
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from utils.azure_storage import get_storage_manager


class PersistentTemplateDB:
    """
    Template database that persists data in Azure Blob Storage
    Replaces the local SQLite database for cloud deployment
    """
    
    def __init__(self):
        """Initialize persistent template database"""
        self.storage = get_storage_manager()
        self.templates_cache = None
        self.cache_timestamp = None
    
    def _get_templates_from_storage(self) -> List[Dict[str, Any]]:
        """Get templates from persistent storage with caching"""
        # Use cache if available and recent (within 5 minutes)
        if (self.templates_cache is not None and 
            self.cache_timestamp is not None and 
            (datetime.now() - self.cache_timestamp).seconds < 300):
            return self.templates_cache
        
        # Fetch from storage
        templates = self.storage.get_template_metadata()
        
        # Update cache
        self.templates_cache = templates
        self.cache_timestamp = datetime.now()
        
        return templates
    
    def _save_templates_to_storage(self, templates: List[Dict[str, Any]]) -> bool:
        """Save templates to persistent storage and update cache"""
        success = self.storage.save_template_metadata(templates)
        
        if success:
            # Update cache
            self.templates_cache = templates
            self.cache_timestamp = datetime.now()
        
        return success
    
    def add_template(self, template_id: str, name: str, filename: str, file_type: str, format_data: Dict[str, Any], cai_contact: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a new template to persistent storage

        Args:
            template_id: Unique template identifier
            name: Template display name
            filename: Original filename
            file_type: File type (docx, doc, etc.)
            format_data: Template formatting data
            cai_contact: CAI contact information extracted from template

        Returns:
            bool: Success status
        """
        try:
            # Get current templates
            templates = self._get_templates_from_storage()

            # Create new template entry
            new_template = {
                'id': template_id,
                'name': name,
                'filename': filename,
                'file_type': file_type,
                'upload_date': datetime.now().isoformat(),
                'format_data': format_data,
                'cai_contact': cai_contact if cai_contact else None
            }
            
            # Remove existing template with same ID (if any)
            templates = [t for t in templates if t['id'] != template_id]
            
            # Add new template
            templates.append(new_template)
            
            # Save to storage
            success = self._save_templates_to_storage(templates)
            
            if success:
                print(f"✅ Template '{name}' added to persistent storage")
            else:
                print(f"❌ Failed to add template '{name}' to persistent storage")
            
            return success
            
        except Exception as e:
            print(f"❌ Error adding template: {e}")
            return False
    
    def get_all_templates(self) -> List[Dict[str, Any]]:
        """
        Get all templates from persistent storage

        Returns:
            List of template dictionaries (including format_data for skill matrix)
        """
        try:
            templates = self._get_templates_from_storage()

            # Return templates with format_data for skill matrix feature
            return [
                {
                    'id': t['id'],
                    'name': t['name'],
                    'filename': t['filename'],
                    'file_type': t['file_type'],
                    'upload_date': t['upload_date'],
                    'format_data': t.get('format_data', {}),  # Include format_data for skill matrix
                    'cai_contact': t.get('cai_contact', None)  # Include CAI contact if present
                }
                for t in templates
            ]

        except Exception as e:
            print(f"❌ Error getting templates: {e}")
            return []
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific template by ID
        
        Args:
            template_id: Template identifier
            
        Returns:
            Template dictionary with all data, or None if not found
        """
        try:
            templates = self._get_templates_from_storage()
            
            for template in templates:
                if template['id'] == template_id:
                    return template
            
            print(f"⚠️ Template not found: {template_id}")
            return None
            
        except Exception as e:
            print(f"❌ Error getting template: {e}")
            return None
    
    def delete_template(self, template_id: str) -> bool:
        """
        Delete a template from persistent storage
        
        Args:
            template_id: Template identifier
            
        Returns:
            bool: Success status
        """
        try:
            # Get current templates
            templates = self._get_templates_from_storage()
            
            # Find template to delete
            template_to_delete = None
            for template in templates:
                if template['id'] == template_id:
                    template_to_delete = template
                    break
            
            if not template_to_delete:
                print(f"⚠️ Template not found for deletion: {template_id}")
                return False
            
            # Remove from list
            templates = [t for t in templates if t['id'] != template_id]
            
            # Save updated list
            metadata_success = self._save_templates_to_storage(templates)
            
            # Delete template file from storage
            file_success = self.storage.delete_template_file(template_id, template_to_delete['filename'])
            
            if metadata_success and file_success:
                print(f"✅ Template '{template_to_delete['name']}' deleted from persistent storage")
                return True
            else:
                print(f"⚠️ Partial deletion of template '{template_to_delete['name']}'")
                return False
            
        except Exception as e:
            print(f"❌ Error deleting template: {e}")
            return False
    
    def upload_template_file(self, template_id: str, local_file_path: str, filename: str) -> bool:
        """
        Upload template file to persistent storage
        
        Args:
            template_id: Template identifier
            local_file_path: Path to local template file
            filename: Original filename
            
        Returns:
            bool: Success status
        """
        return self.storage.upload_template_file(template_id, local_file_path, filename)
    
    def download_template_file(self, template_id: str, filename: str, local_path: str) -> bool:
        """
        Download template file from persistent storage
        
        Args:
            template_id: Template identifier
            filename: Original filename
            local_path: Where to save the file locally
            
        Returns:
            bool: Success status
        """
        return self.storage.download_template_file(template_id, filename, local_path)
    
    def clear_cache(self):
        """Clear the templates cache"""
        self.templates_cache = None
        self.cache_timestamp = None
        print("🧹 Template cache cleared")
    
    def update_template_cai_contact(self, template_id: str, cai_contact: Dict[str, Any]) -> bool:
        """
        Update CAI contact information for a template
        
        Args:
            template_id: Template identifier
            cai_contact: CAI contact dictionary with name, phone, email, state
            
        Returns:
            bool: Success status
        """
        try:
            # Get current templates
            templates = self._get_templates_from_storage()
            
            # Find and update the template
            updated = False
            for template in templates:
                if template['id'] == template_id:
                    template['cai_contact'] = cai_contact
                    updated = True
                    print(f"Updated CAI contact for template '{template['name']}'")
                    break

            if not updated:
                print(f"WARNING: Template not found for CAI contact update: {template_id}")
                return False

            # Save updated list
            success = self._save_templates_to_storage(templates)

            if success:
                # Clear cache to force reload
                self.clear_cache()

            return success

        except Exception as e:
            print(f"ERROR: Error updating template CAI contact: {e}")
            return False


class PersistentCAIContactDB:
    """
    CAI Contact database that persists data in Azure Blob Storage
    Replaces the local file storage for cloud deployment
    """
    
    def __init__(self):
        """Initialize persistent CAI contact database"""
        self.storage = get_storage_manager()
    
    def save_contact(self, contact_data: Dict[str, Any]) -> bool:
        """
        Save CAI contact data to persistent storage
        
        Args:
            contact_data: Contact information dictionary
            
        Returns:
            bool: Success status
        """
        try:
            # Validate contact data
            validated_data = {
                "name": str(contact_data.get("name", "")).strip(),
                "phone": str(contact_data.get("phone", "")).strip(),
                "email": str(contact_data.get("email", "")).strip(),
                "last_updated": datetime.now().isoformat()
            }
            
            success = self.storage.save_cai_contact(validated_data)
            
            if success:
                print(f"✅ CAI contact saved: {validated_data['name']}")
            else:
                print("❌ Failed to save CAI contact")
            
            return success
            
        except Exception as e:
            print(f"❌ Error saving CAI contact: {e}")
            return False
    
    def get_contact(self) -> Dict[str, Any]:
        """
        Get CAI contact data from persistent storage
        
        Returns:
            Dict: Contact information or default empty contact
        """
        try:
            contact_data = self.storage.get_cai_contact()
            
            # Remove internal fields for API response
            api_data = {
                "name": contact_data.get("name", ""),
                "phone": contact_data.get("phone", ""),
                "email": contact_data.get("email", "")
            }
            
            return api_data
            
        except Exception as e:
            print(f"❌ Error getting CAI contact: {e}")
            return {"name": "", "phone": "", "email": ""}


# Singleton instances
_template_db = None
_cai_contact_db = None

def get_persistent_template_db() -> PersistentTemplateDB:
    """Get or create the singleton persistent template database"""
    global _template_db
    if _template_db is None:
        _template_db = PersistentTemplateDB()
    return _template_db

def get_persistent_cai_contact_db() -> PersistentCAIContactDB:
    """Get or create the singleton persistent CAI contact database"""
    global _cai_contact_db
    if _cai_contact_db is None:
        _cai_contact_db = PersistentCAIContactDB()
    return _cai_contact_db
