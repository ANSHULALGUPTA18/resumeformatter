import React, { useEffect, useState } from 'react';
import './ResumeUploadPhase.css';
import { getCaiContact, saveCaiContact, deleteCaiContact, getTemplateCaiContacts } from '../services/api';
import CAIContactManager from './CAIContactManager';

const ResumeUploadPhase = ({ selectedTemplate, templates, onFormatSuccess, onBack, isFormatting, setIsFormatting }) => {
  const [files, setFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [caiContact, setCaiContact] = useState({ name: '', phone: '', email: '' });
  const [selectedContacts, setSelectedContacts] = useState([]);
  const [selectedContactIds, setSelectedContactIds] = useState([]);
  const [showCaiEditor, setShowCaiEditor] = useState(false);
  const [savingCai, setSavingCai] = useState(false);
  const [editingContactId, setEditingContactId] = useState(null);
  const [fileStatuses, setFileStatuses] = useState({});
  const [showHelp, setShowHelp] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [allContacts, setAllContacts] = useState([]);

  const selectedTemplateData = templates.find(t => t.id === selectedTemplate);

  // Load stored CAI contact and all contacts on mount
  useEffect(() => {
    (async () => {
      try {
        const res = await getCaiContact();
        if (res?.success && res?.contact && (res.contact.name || res.contact.email)) {
          // Only add to list if contact has actual data
          const contactWithId = { id: 1, ...res.contact };
          setAllContacts([contactWithId]);
          // Don't auto-select, let user choose
        }
      } catch (e) {
        console.error('Error loading CAI contact:', e);
      }
    })();
  }, []);

  // Load CAI contact from selected template when template changes
  useEffect(() => {
    if (selectedTemplate) {
      (async () => {
        try {
          console.log(`🔍 Loading CAI contact from template: ${selectedTemplate}`);
          const res = await getTemplateCaiContacts(selectedTemplate);
          
          if (res?.success && res?.contacts && res.contacts.length > 0) {
            const templateContact = res.contacts[0];
            console.log('✅ CAI Contact detected from template:', templateContact);
            
            // Add template contact to all contacts list if not already there
            setAllContacts(prev => {
              const exists = prev.some(c => 
                c.name === templateContact.name && 
                c.email === templateContact.email
              );
              if (!exists) {
                return [...prev, { ...templateContact, id: Date.now() }];
              }
              return prev;
            });
            
            // Auto-select the template contact
            setSelectedContacts([templateContact]);
            
            // Show notification to user
            if (templateContact.name) {
              console.log(`📋 Auto-selected CAI Contact: ${templateContact.name}`);
            }
          } else {
            console.log('⚠️ No CAI contact found in template');
          }
        } catch (e) {
          console.error('Error loading template CAI contact:', e);
        }
      })();
    }
  }, [selectedTemplate]);

  const toggleDropdown = () => {
    setIsDropdownOpen(!isDropdownOpen);
  };

  const toggleContactSelection = (contact) => {
    setSelectedContacts(prev => {
      const isSelected = prev.some(c => c.id === contact.id);
      if (isSelected) {
        return prev.filter(c => c.id !== contact.id);
      } else {
        return [...prev, contact];
      }
    });
  };

  const handleFileSelect = (e) => {
    const newFiles = Array.from(e.target.files);
    setFiles(prev => [...prev, ...newFiles]);
    // Set initial status for each file
    const newStatuses = {};
    newFiles.forEach((file, idx) => {
      newStatuses[files.length + idx] = { status: 'ready', message: 'Ready to format' };
    });
    setFileStatuses(prev => ({ ...prev, ...newStatuses }));
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFiles = Array.from(e.dataTransfer.files);
    setFiles(prev => [...prev, ...droppedFiles]);
    // Set initial status for each file
    const newStatuses = {};
    droppedFiles.forEach((file, idx) => {
      newStatuses[files.length + idx] = { status: 'ready', message: 'Ready to format' };
    });
    setFileStatuses(prev => ({ ...prev, ...newStatuses }));
    // Show AI detection banner
    setIsProcessing(true);
    setTimeout(() => setIsProcessing(false), 2000);
  };

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleFormat = async () => {
    if (files.length === 0) {
      alert('Please upload at least one resume');
      return;
    }

    setIsFormatting(true);
    const formData = new FormData();
    formData.append('template_id', selectedTemplate);
    files.forEach(file => {
      formData.append('resume_files', file);
    });
    
    // Send ALL selected CAI contacts (multiple)
    if (selectedContacts && selectedContacts.length > 0) {
      formData.append('cai_contacts', JSON.stringify(selectedContacts));
      formData.append('edit_cai_contact', 'true');
    } else if (caiContact.name || caiContact.phone || caiContact.email) {
      // Backward compatibility: single contact
      formData.append('cai_contact', JSON.stringify(caiContact));
      formData.append('edit_cai_contact', 'true');
    }

    try {
      const response = await fetch('/api/format', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      if (data.success) {
        onFormatSuccess(data.files);
      } else {
        alert(data.message || 'Formatting failed');
        setIsFormatting(false);
      }
    } catch (error) {
      alert('Error formatting resumes');
      setIsFormatting(false);
    }
  };

  const handleOpenCai = () => setShowCaiEditor(true);
  const handleCloseCai = () => setShowCaiEditor(false);
  const handleChangeCai = (e) => {
    const { name, value } = e.target;
    setCaiContact(prev => ({ ...prev, [name]: value }));
  };
  const handleSaveCai = async () => {
    // Validate that contact has at least a name
    if (!caiContact.name || caiContact.name.trim() === '') {
      alert('Please enter a contact name');
      return;
    }

    setSavingCai(true);
    try {
      const res = await saveCaiContact(caiContact);
      if (!res?.success) throw new Error('Save failed');
      
      // Check if we're editing an existing contact
      if (editingContactId) {
        // Update existing contact
        const updatedContact = { id: editingContactId, ...res.contact };
        setAllContacts(prev => prev.map(c => c.id === editingContactId ? updatedContact : c));
        setSelectedContacts(prev => prev.map(c => c.id === editingContactId ? updatedContact : c));
        setEditingContactId(null);
      } else {
        // Add new contact
        const newContactId = Date.now();
        const newContact = { id: newContactId, ...res.contact };
        setAllContacts(prev => [...prev, newContact]);
        setSelectedContacts(prev => [...prev, newContact]);
        setSelectedContactIds(prev => [...prev, newContactId]);
      }
      
      // Clear the form for next contact
      setCaiContact({ name: '', phone: '', email: '' });
      
      setShowCaiEditor(false);
    } catch (e) {
      alert('Failed to save CAI Contact');
    } finally {
      setSavingCai(false);
    }
  };

  return (
    <div className="resume-upload-phase">
      {/* Navigation Arrows - Below Navbar */}
      <div className="nav-arrows-container">
        <button className="nav-arrow-left" onClick={onBack} aria-label="Go back">
          <i className="fas fa-chevron-left"></i>
        </button>
        <button className="nav-arrow-right" onClick={handleFormat} disabled={files.length === 0} aria-label="Next">
          <i className="fas fa-chevron-right"></i>
        </button>
      </div>

      {/* Main Content Container */}
      <div className="upload-content-container">
        {/* CAI Contacts Dropdown */}
      <div className="cai-dropdown-wrapper">
        <button className="cai-dropdown-toggle-new" onClick={toggleDropdown}>
          <i className="fas fa-users"></i>
          <span className="dropdown-label">CAI Contacts ({selectedContacts.length})</span>
          <span className="contact-badge">{selectedContacts.length}</span>
          <i className={`fas fa-chevron-down dropdown-arrow-icon ${isDropdownOpen ? 'open' : ''}`}></i>
        </button>
        
        {isDropdownOpen && (
          <div className="cai-dropdown-panel">
            <div className="dropdown-panel-header">
              <span>Select Contacts</span>
              <button className="add-contact-btn-new" onClick={() => { setShowCaiEditor(true); setIsDropdownOpen(false); }}>
                + Add Contact
              </button>
            </div>
            {allContacts.length > 0 ? (
              <div className="cai-contacts-list-new">
                {allContacts.map((contact) => {
                  const isSelected = selectedContacts.some(c => c.id === contact.id);
                  return (
                    <div 
                      key={contact.id} 
                      className="cai-contact-item-new"
                    >
                      <input 
                        type="checkbox" 
                        className="contact-checkbox-new"
                        checked={isSelected}
                        onChange={() => toggleContactSelection(contact)}
                      />
                      <div className="contact-info-new" onClick={() => toggleContactSelection(contact)}>
                        <div className="contact-name-new">
                          {contact.name}{contact.state ? ` - ${contact.state}` : ''}
                        </div>
                        <div className="contact-details-new">
                          {contact.email} • {contact.phone}
                        </div>
                      </div>
                      <div className="contact-actions-new">
                        <button 
                          className="contact-edit-btn"
                          onClick={(e) => {
                            e.stopPropagation();
                            setCaiContact({ name: contact.name, phone: contact.phone, email: contact.email });
                            setEditingContactId(contact.id);
                            setShowCaiEditor(true);
                          }}
                          title="Edit contact"
                        >
                          <i className="fas fa-edit"></i>
                        </button>
                        <button 
                          className="contact-delete-btn"
                          onClick={async (e) => {
                            e.stopPropagation();
                            if (window.confirm(`Delete contact "${contact.name}"?`)) {
                              try {
                                // Call API to delete contact from backend
                                await deleteCaiContact();
                                // Update local state
                                setAllContacts(prev => prev.filter(c => c.id !== contact.id));
                                setSelectedContacts(prev => prev.filter(c => c.id !== contact.id));
                                setSelectedContactIds(prev => prev.filter(id => id !== contact.id));
                              } catch (err) {
                                console.error('Failed to delete contact:', err);
                                alert('Failed to delete contact. Please try again.');
                              }
                            }
                          }}
                          title="Delete contact"
                        >
                          <i className="fas fa-trash"></i>
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="no-contacts-message-new">
                No contacts available. Click "Add Contact" to create one.
              </div>
            )}
          </div>
        )}
      </div>

      {/* Upload Container */}
      <div className="upload-container-new">
        <div
          className={`dropzone-new ${isDragging ? 'dragging' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => document.getElementById('file-upload').click()}
        >
          <div className="cloud-icon">
            <i className="fas fa-cloud-upload-alt"></i>
          </div>
          <p className="dropzone-text-primary">
            Drag or Drop <span className="highlight-text">Your Resume Here</span> or <span className="highlight-text">Upload</span> an existing file
          </p>
          <p className="dropzone-text-secondary">
            Upto 10 resumes you can upload here
          </p>
          <button className="upload-button-new" onClick={(e) => { e.stopPropagation(); document.getElementById('file-upload').click(); }}>
            Upload Resume
          </button>
        </div>
      </div>

      <input
        id="file-upload"
        type="file"
        multiple
        accept=".pdf,.docx,.doc"
        onChange={handleFileSelect}
        style={{ display: 'none' }}
      />

      {/* File List */}
      {files.length > 0 && (
        <div className="uploaded-files-new">
          {files.map((file, index) => (
            <div key={index} className="file-item-new">
              <i className="far fa-file-alt file-icon-new"></i>
              <div className="file-name-new">{file.name}</div>
              <button className="remove-file-btn-new" onClick={() => removeFile(index)}>
                ×
              </button>
            </div>
          ))}
        </div>
      )}
      </div>

      {/* Bottom Action Bar */}
      <div className="bottom-action-bar">
        <button className="btn-cancel-new" onClick={onBack}>
          Cancel
        </button>
        <button
          className="btn-format-new"
          onClick={handleFormat}
          disabled={isFormatting || files.length === 0}
        >
          {isFormatting ? (
            <>
              <span className="spinner-new"></span>
              Formatting...
            </>
          ) : (
            'Format'
          )}
        </button>
      </div>

      {/* CAI Contact Modal */}
      {showCaiEditor && (
        <div className="modal-overlay" onClick={handleCloseCai}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">Edit CAI Contact</div>
            <div className="modal-body">
              <div className="form-row">
                <label>Name</label>
                <input name="name" value={caiContact.name} onChange={handleChangeCai} placeholder="Full name" />
              </div>
              <div className="form-row">
                <label>Phone</label>
                <input name="phone" value={caiContact.phone} onChange={handleChangeCai} placeholder="Phone number" />
              </div>
              <div className="form-row">
                <label>Email</label>
                <input name="email" value={caiContact.email} onChange={handleChangeCai} placeholder="name@cai.io" />
              </div>
            </div>
            <div className="modal-actions">
              <button className="btn-secondary" onClick={handleCloseCai} disabled={savingCai}>Cancel</button>
              <button className="btn-primary" onClick={handleSaveCai} disabled={savingCai}>
                {savingCai ? 'Saving…' : 'Save'}
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* CAI Contact Manager Component */}
      <div style={{ display: 'none' }}>
        <CAIContactManager 
          onSelectContacts={(contacts, contactIds) => {
            setSelectedContacts(contacts);
            setSelectedContactIds(contactIds);
            if (contacts.length > 0) {
              setCaiContact({
                name: contacts[0].name,
                phone: contacts[0].phone,
                email: contacts[0].email
              });
            }
          }}
          selectedContactIds={selectedContactIds}
          templateId={selectedTemplate}
        />
      </div>
    </div>
  );
}

export default ResumeUploadPhase;
