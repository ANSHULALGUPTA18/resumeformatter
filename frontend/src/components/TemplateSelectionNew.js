import React, { useState, useEffect, useRef } from 'react';
import './TemplateSelectionNew.css';
import OnlyOfficeTemplateEditor from './OnlyOfficeTemplateEditor';

const TemplateSelectionNew = ({ templates, selectedTemplate, onSelect, onDelete, onUpload, darkMode, onBack }) => {
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [favorites, setFavorites] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState('available');
  const scrollRef = useRef(null);
  const [editingTemplate, setEditingTemplate] = useState(null);
  const [showEditMenu, setShowEditMenu] = useState(null);
  const [renamingTemplate, setRenamingTemplate] = useState(null);
  const [newTemplateName, setNewTemplateName] = useState('');

  // Load favorites from localStorage
  useEffect(() => {
    const savedFavorites = localStorage.getItem('templateFavorites');
    if (savedFavorites) {
      setFavorites(JSON.parse(savedFavorites));
    }
  }, []);

  // Toggle favorite status
  const toggleFavorite = (templateId, e) => {
    e.stopPropagation();
    const newFavorites = favorites.includes(templateId)
      ? favorites.filter(id => id !== templateId)
      : [...favorites, templateId];
    setFavorites(newFavorites);
    localStorage.setItem('templateFavorites', JSON.stringify(newFavorites));
  };

  // Filter templates
  const filteredTemplates = templates.filter(template => {
    return template.name.toLowerCase().includes(searchQuery.toLowerCase());
  });

  // Get current templates based on active tab
  const currentTemplates = activeTab === 'available' 
    ? filteredTemplates 
    : filteredTemplates.filter(t => favorites.includes(t.id));

  // Scroll functions - scroll by width of one card plus gap
  const scrollLeft = () => {
    if (scrollRef.current) {
      const cardWidth = 270; // card width
      const gap = 24; // gap between cards
      scrollRef.current.scrollBy({ left: -(cardWidth + gap), behavior: 'smooth' });
    }
  };

  const scrollRight = () => {
    if (scrollRef.current) {
      const cardWidth = 270;
      const gap = 24;
      scrollRef.current.scrollBy({ left: cardWidth + gap, behavior: 'smooth' });
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      alert('Please select a file');
      return;
    }

    setUploading(true);
    // Use filename without extension as template name
    const templateName = file.name.replace(/\.[^/.]+$/, '');
    const formData = new FormData();
    formData.append('template_name', templateName);
    formData.append('template_file', file);

    try {
      const response = await fetch('/api/templates', {
        method: 'POST',
        body: formData
      });

      const contentType = response.headers.get('content-type') || '';
      if (!response.ok) {
        const errText = contentType.includes('application/json')
          ? JSON.stringify(await response.json())
          : await response.text();
        alert(`Upload failed (HTTP ${response.status}).\n${errText || 'No error body'}`);
        return;
      }

      const data = contentType.includes('application/json') ? await response.json() : { success: false, message: 'Unexpected response format' };
      if (data.success) {
        alert('Template uploaded successfully!');
        setShowUploadModal(false);
        setFile(null);
        onUpload();
      } else {
        alert(data.message || 'Upload failed');
      }
    } catch (error) {
      console.error('Upload error', error);
      alert(`Error uploading template.\n${error?.message || ''}`);
    } finally {
      setUploading(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    const fileName = droppedFile.name.toLowerCase();
    if (droppedFile && (fileName.endsWith('.docx') || fileName.endsWith('.doc') || fileName.endsWith('.pdf') || fileName.endsWith('.odt') || fileName.endsWith('.rtf'))) {
      setFile(droppedFile);
      setShowUploadModal(true);
    } else {
      alert('Please drop a valid template file (.docx, .doc, .pdf, .odt, or .rtf)');
    }
  };

  const handleRename = async (e) => {
    e.preventDefault();
    if (!newTemplateName.trim()) {
      alert('Please enter a template name');
      return;
    }

    try {
      const response = await fetch(`/api/templates/${renamingTemplate.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: newTemplateName.trim() }),
      });

      if (!response.ok) {
        throw new Error(`Rename failed: ${response.statusText}`);
      }

      const data = await response.json();
      if (data.success) {
        alert('Template renamed successfully!');
        setRenamingTemplate(null);
        setNewTemplateName('');
        onUpload(); // Refresh templates
      } else {
        alert(data.message || 'Rename failed');
      }
    } catch (error) {
      console.error('Rename error:', error);
      alert(`Error renaming template: ${error.message}`);
    }
  };

  return (
    <div className="template-library">
      {/* Page Header */}
      <div className="page-header">
        <h1 className="page-title">Choose Resume Templates</h1>
      </div>

      {/* Search Section */}
      <div className="search-section">
        <div className="search-bar">
          <i className="fas fa-search search-icon"></i>
          <input
            type="text"
            className="search-input"
            placeholder="Search templates by name"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs">
        <div
          className={`tab ${activeTab === 'available' ? 'active' : ''}`}
          onClick={() => setActiveTab('available')}
        >
          Available Templates
        </div>
        <div
          className={`tab ${activeTab === 'favorites' ? 'active' : ''}`}
          onClick={() => setActiveTab('favorites')}
        >
          Favorite Templates
        </div>
      </div>

      {/* Templates Container */}
      <div className="templates-container">
        <div className="scroll-wrapper">
          {currentTemplates.length > 0 && (
            <button className="scroll-btn scroll-btn-left" onClick={scrollLeft} aria-label="Scroll left">
              <i className="fas fa-chevron-left"></i>
            </button>
          )}

          <div className="horizontal-scroll-container" ref={scrollRef}>
            <div className="template-row">
              {/* Add New Template Card - Always First and Always Visible */}
              <div className="add-template-card" onClick={() => setShowUploadModal(true)}>
                <i className="fas fa-plus add-template-icon"></i>
                <div className="add-template-text">Add New Template</div>
              </div>

              {currentTemplates.length === 0 ? (
                <div className="empty-state-inline">
                  <i className="far fa-heart"></i>
                  <h3>{activeTab === 'favorites' ? 'No favorites yet' : 'No templates found'}</h3>
                  <p>{activeTab === 'favorites' ? 'Click the star icon on any template to add it here' : searchQuery ? 'Try adjusting your search' : 'Click "Add New Template" to get started'}</p>
                </div>
              ) : (
                currentTemplates.map((template) => (
                  <div key={template.id} className="template-card" onClick={() => onSelect(template.id)}>
                    <div className="template-preview">
                      <img
                        src={`/api/templates/${template.id}/thumbnail?t=${Date.now()}`}
                        alt={template.name}
                        className="template-image"
                        onError={(e) => {
                          e.currentTarget.onerror = null;
                          e.currentTarget.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 250"%3E%3Crect fill="%23e5e7eb" width="200" height="250"/%3E%3Cpath d="M60 50h80v8H60zm0 20h80v8H60zm0 20h80v8H60zm0 20h60v8H60z" fill="%23cbd5e1"/%3E%3Cpath d="M70 130l20-20 14 14 26-26 20 20v32H70z" fill="%23cbd5e1"/%3E%3C/svg%3E';
                          e.currentTarget.classList.add('template-placeholder-img');
                        }}
                      />
                    </div>
                    <div className="template-footer">
                      <div className="template-info">
                        <div className="template-name">{template.name}</div>
                        <div className="doc-type">Pdf Docx</div>
                      </div>
                    </div>
                    <button
                      className={`favorite-btn ${favorites.includes(template.id) ? 'favorited' : ''}`}
                      onClick={(e) => toggleFavorite(template.id, e)}
                      title={favorites.includes(template.id) ? 'Remove from favorites' : 'Add to favorites'}
                    >
                      <i className="fas fa-star"></i>
                    </button>
                    <div className="edit-menu-container">
                      <button
                        className="edit-btn-new"
                        onClick={(e) => {
                          e.stopPropagation();
                          setShowEditMenu(showEditMenu === template.id ? null : template.id);
                        }}
                        title="Edit options"
                      >
                        <i className="fas fa-edit"></i>
                      </button>
                      {showEditMenu === template.id && (
                        <div className="edit-dropdown-menu" onClick={(e) => e.stopPropagation()}>
                          <button
                            className="edit-menu-item"
                            onClick={(e) => {
                              e.stopPropagation();
                              setNewTemplateName(template.name);
                              setRenamingTemplate(template);
                              setShowEditMenu(null);
                            }}
                          >
                            <i className="fas fa-i-cursor"></i>
                            <span>Edit Name</span>
                          </button>
                          <button
                            className="edit-menu-item"
                            onClick={(e) => {
                              e.stopPropagation();
                              setEditingTemplate(template);
                              setShowEditMenu(null);
                            }}
                          >
                            <i className="fas fa-file-edit"></i>
                            <span>Edit Template</span>
                          </button>
                        </div>
                      )}
                    </div>
                    <button
                      className="delete-btn-new"
                      onClick={async (e) => {
                        e.stopPropagation();
                        if (window.confirm(`Are you sure you want to delete "${template.name}"? This action cannot be undone.`)) {
                          try {
                            const result = await onDelete(template.id);
                            if (result && result.success) {
                              // Remove from favorites if present
                              if (favorites.includes(template.id)) {
                                const newFavorites = favorites.filter(id => id !== template.id);
                                setFavorites(newFavorites);
                                localStorage.setItem('templateFavorites', JSON.stringify(newFavorites));
                              }
                            }
                          } catch (error) {
                            console.error('Error deleting template:', error);
                            alert('Failed to delete template. Please try again.');
                          }
                        }
                      }}
                      title="Delete template"
                    >
                      <i className="fas fa-trash-alt"></i>
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>

          {currentTemplates.length > 0 && (
            <button className="scroll-btn scroll-btn-right" onClick={scrollRight} aria-label="Scroll right">
              <i className="fas fa-chevron-right"></i>
            </button>
          )}
        </div>
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="modal-overlay-new" onClick={() => setShowUploadModal(false)}>
          <div className="modal-content-new" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header-new">
              <h3>📤 Upload New Template</h3>
              <button className="close-btn-new" onClick={() => setShowUploadModal(false)}>×</button>
            </div>
            <form onSubmit={handleUpload} className="upload-form-new">
              <div className="form-group-new">
                <div className="file-input-wrapper-new" onDragOver={handleDragOver} onDrop={handleDrop}>
                  <div className="upload-icon">
                    <i className="fas fa-cloud-upload-alt"></i>
                  </div>
                  <p className="upload-text">Drag and drop your template files here</p>
                  <p className="upload-hint" style={{fontSize: '13px', color: '#9ca3af', marginTop: '8px'}}>
                    Supports: <strong>.DOCX, .DOC, .PDF, .ODT, .RTF</strong> • ODT/RTF/DOC files auto-convert to DOCX
                  </p>
                  <input
                    type="file"
                    accept=".docx,.doc,.pdf,.odt,.rtf"
                    onChange={(e) => setFile(e.target.files[0])}
                    required
                    id="file-input-new"
                  />
                  <label htmlFor="file-input-new" className="browse-files-btn">
                    <i className="fas fa-folder-open"></i> Browse Files
                  </label>
                </div>
              </div>
              
              {file && (
                <div className="selected-files">
                  <h4>Selected Files</h4>
                  <div className="file-item">
                    <i className="fas fa-file-alt file-icon"></i>
                    <div className="file-info">
                      <div className="file-name">{file.name}</div>
                      <div className="file-size">{(file.size / 1024).toFixed(2)} KB</div>
                    </div>
                    <button 
                      type="button" 
                      className="remove-file-btn" 
                      onClick={() => setFile(null)}
                    >
                      ×
                    </button>
                  </div>
                </div>
              )}
              
              <div className="form-actions-new">
                <button type="button" className="btn-cancel-new" onClick={() => setShowUploadModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-format-new" disabled={uploading || !file}>
                  {uploading ? 'Uploading...' : 'Upload Template'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Rename Modal */}
      {renamingTemplate && (
        <div className="modal-overlay-new" onClick={() => setRenamingTemplate(null)}>
          <div className="modal-content-new rename-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header-new">
              <h3>✏️ Rename Template</h3>
              <button className="close-btn-new" onClick={() => setRenamingTemplate(null)}>×</button>
            </div>
            <form onSubmit={handleRename} className="upload-form-new">
              <div className="form-group-new">
                <label htmlFor="template-name" className="form-label">Template Name</label>
                <input
                  type="text"
                  id="template-name"
                  className="text-input-new"
                  value={newTemplateName}
                  onChange={(e) => setNewTemplateName(e.target.value)}
                  placeholder="Enter new template name"
                  autoFocus
                  required
                />
              </div>
              <div className="form-actions-new">
                <button type="button" className="btn-cancel-new" onClick={() => setRenamingTemplate(null)}>
                  Cancel
                </button>
                <button type="submit" className="btn-format-new">
                  Save Name
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Template Editor Modal */}
      {editingTemplate && (
        <OnlyOfficeTemplateEditor
          template={editingTemplate}
          onClose={() => setEditingTemplate(null)}
          onSave={() => {
            // Refresh templates after save
            onUpload();
            setEditingTemplate(null);
          }}
          darkMode={darkMode}
        />
      )}
    </div>
  );
};

export default TemplateSelectionNew;
