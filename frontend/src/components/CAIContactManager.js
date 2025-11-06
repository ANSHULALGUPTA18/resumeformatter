import React, { useState, useEffect } from 'react';
import './CAIContactManager.css';

const CAIContactManager = ({ onSelectContacts, selectedContactIds = [], templateId }) => {
  const [contacts, setContacts] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingContact, setEditingContact] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    email: ''
  });

  useEffect(() => {
    loadContacts();
  }, []);
  
  useEffect(() => {
    // Load template-specific contacts when template changes
    if (templateId) {
      loadTemplateContacts();
    }
  }, [templateId]);

  const loadContacts = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/cai-contacts');
      const data = await response.json();
      if (data.success) {
        setContacts(data.contacts);
      }
    } catch (error) {
      console.error('Error loading contacts:', error);
    }
  };
  
  const loadTemplateContacts = async () => {
    if (!templateId) return;
    
    try {
      const response = await fetch(`http://localhost:5000/api/templates/${templateId}/cai-contacts`);
      const data = await response.json();
      if (data.success && data.contact_ids.length > 0) {
        // Auto-select template-specific contacts
        if (onSelectContacts) {
          onSelectContacts(data.contacts, data.contact_ids);
        }
      }
    } catch (error) {
      console.error('Error loading template contacts:', error);
    }
  };
  
  const saveTemplateContacts = async (contactIds) => {
    if (!templateId) return;
    
    try {
      await fetch(`http://localhost:5000/api/templates/${templateId}/cai-contacts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ contact_ids: contactIds })
      });
    } catch (error) {
      console.error('Error saving template contacts:', error);
    }
  };
  
  const toggleContactSelection = (contact) => {
    let newSelectedIds;
    
    if (selectedContactIds.includes(contact.id)) {
      // Deselect
      newSelectedIds = selectedContactIds.filter(id => id !== contact.id);
    } else {
      // Select (add to array)
      newSelectedIds = [...selectedContactIds, contact.id];
    }
    
    const selectedContacts = contacts.filter(c => newSelectedIds.includes(c.id));
    
    if (onSelectContacts) {
      onSelectContacts(selectedContacts, newSelectedIds);
    }
    
    // Save to template mapping
    saveTemplateContacts(newSelectedIds);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const url = editingContact
        ? `http://localhost:5000/api/cai-contacts/${editingContact.id}`
        : 'http://localhost:5000/api/cai-contacts';
      
      const method = editingContact ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        loadContacts();
        setShowAddForm(false);
        setEditingContact(null);
        setFormData({ name: '', phone: '', email: '' });
      }
    } catch (error) {
      console.error('Error saving contact:', error);
    }
  };

  const handleDelete = async (contactId) => {
    if (!window.confirm('Are you sure you want to delete this contact?')) {
      return;
    }
    
    try {
      const response = await fetch(`http://localhost:5000/api/cai-contacts/${contactId}`, {
        method: 'DELETE'
      });
      
      const data = await response.json();
      
      if (data.success) {
        loadContacts();
      }
    } catch (error) {
      console.error('Error deleting contact:', error);
    }
  };

  const handleSetDefault = async (contactId) => {
    try {
      const response = await fetch(`http://localhost:5000/api/cai-contacts/${contactId}/set-default`, {
        method: 'POST'
      });
      
      const data = await response.json();
      
      if (data.success) {
        loadContacts();
      }
    } catch (error) {
      console.error('Error setting default:', error);
    }
  };

  const handleEdit = (contact) => {
    setEditingContact(contact);
    setFormData({
      name: contact.name,
      phone: contact.phone,
      email: contact.email
    });
    setShowAddForm(true);
  };

  const handleCancel = () => {
    setShowAddForm(false);
    setEditingContact(null);
    setFormData({ name: '', phone: '', email: '' });
  };

  return (
    <div className="cai-contact-manager">
      <div className="cai-header">
        <div className="cai-title">
          <span className="cai-icon">👤</span>
          <h3>CAI Contacts</h3>
        </div>
        <button 
          className="cai-add-btn"
          onClick={() => setShowAddForm(!showAddForm)}
        >
          {showAddForm ? '✕ Cancel' : '+ Add Contact'}
        </button>
      </div>

      {showAddForm && (
        <div className="cai-form-card">
          <h4>{editingContact ? 'Edit Contact' : 'New Contact'}</h4>
          <form onSubmit={handleSubmit}>
            <div className="cai-form-group">
              <label>Name *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., John Doe"
                required
              />
            </div>
            <div className="cai-form-group">
              <label>Phone</label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                placeholder="e.g., (555) 123-4567"
              />
            </div>
            <div className="cai-form-group">
              <label>Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="e.g., john@example.com"
              />
            </div>
            <div className="cai-form-actions">
              <button type="button" className="cai-btn-cancel" onClick={handleCancel}>
                Cancel
              </button>
              <button type="submit" className="cai-btn-save">
                {editingContact ? 'Update' : 'Save'} Contact
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="cai-contacts-list">
        {contacts.length === 0 ? (
          <div className="cai-empty-state">
            <span className="empty-icon">📋</span>
            <p>No contacts yet</p>
            <small>Add your first CAI contact to get started</small>
          </div>
        ) : (
          contacts.map(contact => (
            <div 
              key={contact.id}
              className={`cai-contact-card ${selectedContactIds.includes(contact.id) ? 'selected' : ''} ${contact.is_default ? 'default' : ''}`}
              onClick={() => toggleContactSelection(contact)}
            >
              <div className="contact-header">
                <div className="contact-avatar">
                  {contact.name.charAt(0).toUpperCase()}
                </div>
                <div className="contact-info">
                  <h4>{contact.name}</h4>
                  {contact.is_default && <span className="default-badge">Default</span>}
                </div>
                <div className="contact-actions">
                  <button
                    className="action-btn edit"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleEdit(contact);
                    }}
                    title="Edit"
                  >
                    ✏️
                  </button>
                  {!contact.is_default && (
                    <button
                      className="action-btn star"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleSetDefault(contact.id);
                      }}
                      title="Set as default"
                    >
                      ⭐
                    </button>
                  )}
                  <button
                    className="action-btn delete"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(contact.id);
                    }}
                    title="Delete"
                  >
                    🗑️
                  </button>
                </div>
              </div>
              <div className="contact-details">
                {contact.phone && (
                  <div className="detail-item">
                    <span className="detail-icon">📞</span>
                    <span>{contact.phone}</span>
                  </div>
                )}
                {contact.email && (
                  <div className="detail-item">
                    <span className="detail-icon">✉️</span>
                    <span>{contact.email}</span>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default CAIContactManager;
