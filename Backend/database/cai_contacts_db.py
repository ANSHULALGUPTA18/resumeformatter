"""
CAI Contacts Database Manager
Simple JSON-based storage for CAI contacts with template-specific defaults
"""
import json
import os
from models.cai_contact import CAIContact

class CAIContactsDB:
    def __init__(self, db_file='cai_contacts.json', mapping_file='template_cai_mapping.json'):
        self.db_file = os.path.join(os.path.dirname(__file__), db_file)
        self.mapping_file = os.path.join(os.path.dirname(__file__), mapping_file)
        self._ensure_db_exists()
        self._ensure_mapping_exists()
    
    def _ensure_db_exists(self):
        """Create database file if it doesn't exist"""
        if not os.path.exists(self.db_file):
            self._save_data({'contacts': [], 'next_id': 1})
    
    def _load_data(self):
        """Load data from JSON file"""
        try:
            with open(self.db_file, 'r') as f:
                return json.load(f)
        except:
            return {'contacts': [], 'next_id': 1}
    
    def _save_data(self, data):
        """Save data to JSON file"""
        with open(self.db_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_all_contacts(self):
        """Get all CAI contacts"""
        data = self._load_data()
        return [CAIContact.from_dict(c) for c in data['contacts']]
    
    def get_contact(self, contact_id):
        """Get a specific contact by ID"""
        data = self._load_data()
        for c in data['contacts']:
            if c['id'] == contact_id:
                return CAIContact.from_dict(c)
        return None
    
    def add_contact(self, name, phone, email, is_default=False):
        """Add a new contact"""
        data = self._load_data()
        
        # If this is set as default, unset all other defaults
        if is_default:
            for c in data['contacts']:
                c['is_default'] = False
        
        contact = {
            'id': data['next_id'],
            'name': name,
            'phone': phone,
            'email': email,
            'is_default': is_default
        }
        
        data['contacts'].append(contact)
        data['next_id'] += 1
        self._save_data(data)
        
        return CAIContact.from_dict(contact)
    
    def update_contact(self, contact_id, name=None, phone=None, email=None, is_default=None):
        """Update an existing contact"""
        data = self._load_data()
        
        for c in data['contacts']:
            if c['id'] == contact_id:
                if name is not None:
                    c['name'] = name
                if phone is not None:
                    c['phone'] = phone
                if email is not None:
                    c['email'] = email
                if is_default is not None:
                    # If setting as default, unset all others
                    if is_default:
                        for other in data['contacts']:
                            other['is_default'] = False
                    c['is_default'] = is_default
                
                self._save_data(data)
                return CAIContact.from_dict(c)
        
        return None
    
    def delete_contact(self, contact_id):
        """Delete a contact"""
        data = self._load_data()
        data['contacts'] = [c for c in data['contacts'] if c['id'] != contact_id]
        self._save_data(data)
        return True
    
    def get_default_contact(self):
        """Get the default contact"""
        data = self._load_data()
        for c in data['contacts']:
            if c.get('is_default', False):
                return CAIContact.from_dict(c)
        return None
    
    def set_default_contact(self, contact_id):
        """Set a contact as default"""
        return self.update_contact(contact_id, is_default=True)
    
    def _ensure_mapping_exists(self):
        """Create template mapping file if it doesn't exist"""
        if not os.path.exists(self.mapping_file):
            self._save_mapping({'mappings': {}, 'last_updated': None})
    
    def _load_mapping(self):
        """Load template-to-contact mapping"""
        try:
            with open(self.mapping_file, 'r') as f:
                return json.load(f)
        except:
            return {'mappings': {}, 'last_updated': None}
    
    def _save_mapping(self, mapping_data):
        """Save template-to-contact mapping"""
        with open(self.mapping_file, 'w') as f:
            json.dump(mapping_data, f, indent=2)
    
    def get_template_contacts(self, template_id):
        """Get contact IDs for a specific template"""
        mapping = self._load_mapping()
        return mapping.get('mappings', {}).get(str(template_id), [])
    
    def set_template_contacts(self, template_id, contact_ids):
        """Set contact IDs for a specific template (supports multiple)"""
        import datetime
        mapping = self._load_mapping()
        mapping['mappings'][str(template_id)] = contact_ids
        mapping['last_updated'] = datetime.datetime.now().isoformat()
        self._save_mapping(mapping)
        return True
    
    def get_contacts_by_ids(self, contact_ids):
        """Get multiple contacts by their IDs"""
        data = self._load_data()
        contacts = []
        for c in data['contacts']:
            if c['id'] in contact_ids:
                contacts.append(CAIContact.from_dict(c))
        return contacts

# Global instance
cai_contacts_db = CAIContactsDB()
