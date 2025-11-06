import React, { useEffect, useState } from 'react';
import './ResumeUploadPhase.css';
import { getCaiContact, saveCaiContact } from '../services/api';
import CAIContactManager from './CAIContactManager';

const ResumeUploadPhase = ({ selectedTemplate, templates, onFormatSuccess, onBack, isFormatting, setIsFormatting }) => {
  const [files, setFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [caiContact, setCaiContact] = useState({ name: '', phone: '', email: '' });
  const [selectedContacts, setSelectedContacts] = useState([]);
  const [selectedContactIds, setSelectedContactIds] = useState([]);
  const [showCaiEditor, setShowCaiEditor] = useState(false);
  const [savingCai, setSavingCai] = useState(false);
  const [fileStatuses, setFileStatuses] = useState({});
  const [showHelp, setShowHelp] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);

  const selectedTemplateData = templates.find(t => t.id === selectedTemplate);

  // Load stored CAI contact on mount
  useEffect(() => {
    (async () => {
      try {
        const res = await getCaiContact();
        if (res?.success && res?.contact) {
          setCaiContact(res.contact);
        }
      } catch (e) {
        // silent
      }
    })();
  }, []);

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
      const response = await fetch('http://localhost:5000/api/format', {
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
    setSavingCai(true);
    try {
      const res = await saveCaiContact(caiContact);
      if (!res?.success) throw new Error('Save failed');
      setCaiContact(res.contact || caiContact);
      setShowCaiEditor(false);
    } catch (e) {
      alert('Failed to save CAI Contact');
    } finally {
      setSavingCai(false);
    }
  };

  return (
    <div className="resume-upload-phase">
      {/* CAI Contact Manager - Modern UI */}
      <CAIContactManager 
        onSelectContacts={(contacts, contactIds) => {
          setSelectedContacts(contacts);
          setSelectedContactIds(contactIds);
          // Use first contact for backward compatibility
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
      <div className="phase-header">
        <h2>📤 Upload Candidate Resumes</h2>
        <p>Drop your resume files here or click to browse</p>
      </div>

      <div className="selected-template-info">
        <div className="template-badge">
          <span className="badge-label">Selected Template:</span>
          <span className="badge-name">{selectedTemplateData?.name}</span>
        </div>
        <button className="change-template-btn" onClick={onBack}>
          Change Template
        </button>
      </div>

      {/* AI Smart Detection Banner */}
      {isProcessing && (
        <div className="ai-detection-banner">
          <span className="ai-icon">✨</span>
          <span>Smart Skill Extraction in progress… we'll analyze and optimize resumes automatically using AI.</span>
        </div>
      )}

      {/* Help Tooltip */}
      <div className="help-section">
        <button className="help-btn" onClick={() => setShowHelp(!showHelp)} title="Need Assistance?">
          ℹ️ Help
        </button>
        {showHelp && (
          <div className="help-tooltip">
            <h4>📋 Upload Guide</h4>
            <ul>
              <li><strong>Formats:</strong> PDF, DOCX</li>
              <li><strong>Limit:</strong> Up to 100 resumes</li>
              <li><strong>Processing:</strong> ~30 seconds per resume</li>
            </ul>
          </div>
        )}
      </div>

      <div
        className={`dropzone ${isDragging ? 'dragging' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => document.getElementById('file-upload').click()}
      >
        <div className="dropzone-content">
          <div className="upload-icons">
            <span className="file-icon">📄</span>
            <span className="file-icon">📝</span>
          </div>
          <h3>Drag & Drop Resume Files Here</h3>
          <p>Drop up to 100 resumes here or click to browse</p>
          <div className="supported-formats">
            <span className="format-badge">📄 PDF</span>
            <span className="format-badge">📝 DOCX</span>
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
      </div>

      {files.length > 0 && (
        <>
          {/* Batch Actions Toolbar */}
          <div className="batch-toolbar">
            <button className="toolbar-btn" onClick={() => {
              if (selectedFiles.length === files.length) {
                setSelectedFiles([]);
              } else {
                setSelectedFiles(files.map((_, i) => i));
              }
            }}>
              {selectedFiles.length === files.length ? '☐' : '☑'} Select All
            </button>
            <button 
              className="toolbar-btn" 
              disabled={selectedFiles.length === 0}
              onClick={() => {
                setFiles(prev => prev.filter((_, i) => !selectedFiles.includes(i)));
                setSelectedFiles([]);
              }}
            >
              🗑️ Remove Selected
            </button>
            <div className="toolbar-spacer"></div>
            <div className="upload-progress-text">
              Processing {uploadProgress}% complete
            </div>
          </div>

          <div className="uploaded-files">
            <div className="files-header">
              <h3>📋 Uploaded Files ({files.length})</h3>
              <button className="clear-all-btn" onClick={() => { setFiles([]); setSelectedFiles([]); }}>
                Clear All
              </button>
            </div>
            <div className="files-list">
              {files.map((file, index) => {
                const status = fileStatuses[index] || { status: 'ready', message: 'Ready' };
                const statusIcon = {
                  'ready': '🟢',
                  'processing': '🟡',
                  'success': '✅',
                  'error': '🔴'
                }[status.status] || '🟢';

                return (
                  <div 
                    key={index} 
                    className={`file-item ${selectedFiles.includes(index) ? 'selected' : ''}`}
                    onClick={() => {
                      if (selectedFiles.includes(index)) {
                        setSelectedFiles(prev => prev.filter(i => i !== index));
                      } else {
                        setSelectedFiles(prev => [...prev, index]);
                      }
                    }}
                  >
                    <div className="file-checkbox">
                      <input 
                        type="checkbox" 
                        checked={selectedFiles.includes(index)}
                        onChange={() => {}}
                      />
                    </div>
                    <div className="file-icon">
                      {file.name.endsWith('.pdf') ? '📄' : '📝'}
                    </div>
                    <div className="file-details">
                      <div className="file-name">{file.name}</div>
                      <div className="file-meta">
                        <span className="file-size">{(file.size / 1024).toFixed(2)} KB</span>
                        <span className="file-type">{file.name.endsWith('.pdf') ? 'PDF' : 'DOCX'}</span>
                      </div>
                      <div className="file-status">
                        <span className="status-icon">{statusIcon}</span>
                        <span className="status-text">{status.message}</span>
                      </div>
                    </div>
                    <button className="remove-file-btn" onClick={(e) => { e.stopPropagation(); removeFile(index); }}>
                      ×
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        </>
      )}

      <div className="action-buttons">
        <button className="btn-back" onClick={onBack}>
          ← Back to Templates
        </button>
        <button
          className={`btn-format ${files.length > 0 ? 'active' : ''}`}
          onClick={handleFormat}
          disabled={isFormatting || files.length === 0}
        >
          {isFormatting ? (
            <>
              <span className="spinner"></span>
              Formatting {files.length} resume(s)...
            </>
          ) : (
            <>
              ✨ Format {files.length === 0 ? '0 Resumes' : `${files.length} Resume${files.length !== 1 ? 's' : ''}`}
            </>
          )}
        </button>
      </div>

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
    </div>
  );
}

export default ResumeUploadPhase;
