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
      const response = await fetch('/api/cai-contact');
      const data = await response.json();
      if (data.success && data.contact) {
        // Convert single contact to array format for compatibility
        setContacts([{ id: 1, ...data.contact }]);
      } else {
        setContacts([]);
      }
    } catch (error) {
      console.error('Error loading contacts:', error);
      setContacts([]);
    }
  };
  
  const loadTemplateContacts = async () => {
    if (!templateId) return;
    
    try {
      // For now, just load the single global CAI contact
      // In the future, this could be expanded for template-specific contacts
      const response = await fetch('/api/cai-contact');
      const data = await response.json();
      if (data.success && data.contact) {
        const contact = { id: 1, ...data.contact };
        if (onSelectContacts) {
          onSelectContacts([contact], [1]);
        }
      }
    } catch (error) {
      console.error('Error loading template contacts:', error);
    }
  };
  
  const saveTemplateContacts = async (contactIds) => {
    if (!templateId) return;
    
    try {
      // For now, this is a placeholder since we use a single global CAI contact
      // The contact is already saved via the main save function
      console.log(`Template ${templateId} CAI contact mapping: ${contactIds}`);
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
    
    // Validate required fields
    if (!formData.name.trim()) {
      alert('Name is required!');
      return;
    }
    if (!formData.email.trim()) {
      alert('Email is required!');
      return;
    }
    
    try {
      console.log('Saving contact:', formData);
      
      // Always use POST to /api/cai-contact (overwrites existing contact)
      const response = await fetch('/api/cai-contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      console.log('Response status:', response.status);
      const data = await response.json();
      console.log('Response data:', data);
      
      if (data.success) {
        await loadContacts(); // Reload contacts
        setShowAddForm(false);
        setEditingContact(null);
        setFormData({ name: '', phone: '', email: '' });
        alert('✅ Contact saved successfully!');
      } else {
        console.error('Save failed:', data);
        alert('❌ Failed to save contact. Please try again.');
      }
    } catch (error) {
      console.error('Error saving contact:', error);
      alert('❌ Error saving contact. Please check your connection and try again.');
    }
  };

  const handleDelete = async (contactId) => {
    if (!window.confirm('Are you sure you want to clear this contact?')) {
      return;
    }
    
    try {
      // Clear the contact by saving empty data
      const response = await fetch('/api/cai-contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: '', phone: '', email: '' })
      });
      
      const data = await response.json();
      
      if (data.success) {
        loadContacts();
        alert('✅ Contact cleared successfully!');
      }
    } catch (error) {
      console.error('Error clearing contact:', error);
      alert('❌ Error clearing contact.');
    }
  };

  const handleSetDefault = async (contactId) => {
    try {
      // Since we only have one global contact, it's already the default
      console.log(`Contact ${contactId} is already the default (single global contact)`);
      alert('✅ This contact is already set as default!');
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
