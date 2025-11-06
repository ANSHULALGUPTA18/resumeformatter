"""
CAI Contact Routes
API endpoints for managing CAI contacts
"""
from flask import Blueprint, jsonify, request
from database.cai_contacts_db import cai_contacts_db

cai_contact_bp = Blueprint('cai_contact', __name__)

@cai_contact_bp.route('/api/cai-contacts', methods=['GET'])
def get_contacts():
    """Get all CAI contacts"""
    try:
        contacts = cai_contacts_db.get_all_contacts()
        return jsonify({
            'success': True,
            'contacts': [c.to_dict() for c in contacts]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@cai_contact_bp.route('/api/cai-contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    """Get a specific contact"""
    try:
        contact = cai_contacts_db.get_contact(contact_id)
        if contact:
            return jsonify({
                'success': True,
                'contact': contact.to_dict()
            })
        return jsonify({'success': False, 'error': 'Contact not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@cai_contact_bp.route('/api/cai-contacts', methods=['POST'])
def add_contact():
    """Add a new CAI contact"""
    try:
        data = request.json
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        email = data.get('email', '').strip()
        is_default = data.get('is_default', False)
        
        if not name:
            return jsonify({'success': False, 'error': 'Name is required'}), 400
        
        contact = cai_contacts_db.add_contact(name, phone, email, is_default)
        
        return jsonify({
            'success': True,
            'message': 'Contact added successfully',
            'contact': contact.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@cai_contact_bp.route('/api/cai-contacts/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    """Update an existing contact"""
    try:
        data = request.json
        contact = cai_contacts_db.update_contact(
            contact_id,
            name=data.get('name'),
            phone=data.get('phone'),
            email=data.get('email'),
            is_default=data.get('is_default')
        )
        
        if contact:
            return jsonify({
                'success': True,
                'message': 'Contact updated successfully',
                'contact': contact.to_dict()
            })
        return jsonify({'success': False, 'error': 'Contact not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@cai_contact_bp.route('/api/cai-contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    """Delete a contact"""
    try:
        cai_contacts_db.delete_contact(contact_id)
        return jsonify({
            'success': True,
            'message': 'Contact deleted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@cai_contact_bp.route('/api/cai-contacts/default', methods=['GET'])
def get_default_contact():
    """Get the default contact"""
    try:
        contact = cai_contacts_db.get_default_contact()
        if contact:
            return jsonify({
                'success': True,
                'contact': contact.to_dict()
            })
        return jsonify({
            'success': True,
            'contact': None
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@cai_contact_bp.route('/api/cai-contacts/<int:contact_id>/set-default', methods=['POST'])
def set_default_contact(contact_id):
    """Set a contact as default"""
    try:
        contact = cai_contacts_db.set_default_contact(contact_id)
        if contact:
            return jsonify({
                'success': True,
                'message': 'Default contact set successfully',
                'contact': contact.to_dict()
            })
        return jsonify({'success': False, 'error': 'Contact not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@cai_contact_bp.route('/api/templates/<template_id>/cai-contacts', methods=['GET'])
def get_template_contacts(template_id):
    """Get CAI contacts for a specific template"""
    try:
        contact_ids = cai_contacts_db.get_template_contacts(template_id)
        contacts = cai_contacts_db.get_contacts_by_ids(contact_ids)
        return jsonify({
            'success': True,
            'contacts': [c.to_dict() for c in contacts],
            'contact_ids': contact_ids
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@cai_contact_bp.route('/api/templates/<template_id>/cai-contacts', methods=['POST'])
def set_template_contacts(template_id):
    """Set CAI contacts for a specific template (supports multiple)"""
    try:
        data = request.json
        contact_ids = data.get('contact_ids', [])
        
        cai_contacts_db.set_template_contacts(template_id, contact_ids)
        
        return jsonify({
            'success': True,
            'message': 'Template contacts saved successfully',
            'template_id': template_id,
            'contact_ids': contact_ids
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
