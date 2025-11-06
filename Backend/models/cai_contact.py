"""
CAI Contact Model
Stores reusable CAI contact information
"""

class CAIContact:
    """CAI Contact data model"""
    
    def __init__(self, id, name, phone, email, is_default=False):
        self.id = id
        self.name = name
        self.phone = phone
        self.email = email
        self.is_default = is_default
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'is_default': self.is_default
        }
    
    @staticmethod
    def from_dict(data):
        return CAIContact(
            id=data.get('id'),
            name=data.get('name', ''),
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            is_default=data.get('is_default', False)
        )
