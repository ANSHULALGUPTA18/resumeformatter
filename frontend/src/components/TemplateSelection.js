import React, { useState, useEffect } from 'react';
import './TemplateSelection.css';

const TemplateSelection = ({ templates, selectedTemplate, onSelect, onDelete, onUpload, darkMode, onBack }) => {
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [templateName, setTemplateName] = useState('');
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [favorites, setFavorites] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [previewTemplate, setPreviewTemplate] = useState(null);
  const [hoveredTemplate, setHoveredTemplate] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [deleteConfirmId, setDeleteConfirmId] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

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

  // Filter and sort templates
  const filteredTemplates = templates.filter(template => {
    return template.name.toLowerCase().includes(searchQuery.toLowerCase());
  });

  const sortedTemplates = [...filteredTemplates].sort((a, b) => {
    const aFav = favorites.includes(a.id);
    const bFav = favorites.includes(b.id);
    if (aFav && !bFav) return -1;
    if (!aFav && bFav) return 1;
    return 0;
  });

  // Handle drag and drop
  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && (droppedFile.name.endsWith('.docx') || droppedFile.name.endsWith('.pdf') || droppedFile.name.endsWith('.doc'))) {
      setFile(droppedFile);
      setShowUploadModal(true);
    } else {
      alert('Please drop a valid template file (.docx, .pdf, or .doc)');
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!templateName || !file) {
      alert('Please provide template name and file');
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('template_name', templateName);
    formData.append('template_file', file);

    try {
      const response = await fetch('/api/templates', {
        method: 'POST',
        body: formData
      });

      // Handle non-JSON or error responses gracefully
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
        setTemplateName('');
        setFile(null);
        // Refresh template list
        onUpload();
        // Do NOT auto-select the uploaded template; user will choose manually
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

  return (
    <div className={`template-selection ${darkMode ? 'dark-mode' : ''}`}>
      {/* Back Button */}
      {onBack && (
        <button className="back-button" onClick={onBack} title="Go back">
          <span className="back-arrow">←</span>
          <span className="back-text">Back</span>
        </button>
      )}

      <div className="phase-header">
        <h2>🎨 Choose Your Template</h2>
        <p>Select a template to format your resumes or add a new one</p>

        {/* Search Bar */}
        <div className="search-bar">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Search templates by name..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          {searchQuery && (
            <button className="clear-search" onClick={() => setSearchQuery('')}>×</button>
          )}
        </div>
      </div>

      <div className="templates-grid">
        {sortedTemplates.map((template) => {
          return (
          <div
            key={template.id}
            className={`template-card ${selectedTemplate === template.id ? 'selected' : ''} ${favorites.includes(template.id) ? 'favorite' : ''}`}
            onClick={() => onSelect(template.id)}
            onMouseEnter={() => setHoveredTemplate(template.id)}
            onMouseLeave={() => setHoveredTemplate(null)}
          >
            <div className="template-preview">
              <img 
                src={`/api/templates/${template.id}/thumbnail?t=${Date.now()}`}
                alt={template.name}
                className="template-thumbnail-img"
                onError={(e) => {
                  // Fallback to icon if thumbnail fails to load
                  const img = e.currentTarget;
                  img.style.display = 'none';
                  const fallback = img.nextElementSibling;
                  if (fallback && fallback instanceof HTMLElement) {
                    fallback.style.display = 'flex';
                  }
                }}
              />
              <div className="template-thumbnail-fallback" style={{display: 'none'}}>
                <div className="doc-icon">📄</div>
                <div className="doc-lines">
                  <div className="line"></div>
                  <div className="line"></div>
                  <div className="line short"></div>
                </div>
              </div>
            </div>
            {/* Hover Overlay with Actions */}
            {hoveredTemplate === template.id && (
              <div className="hover-overlay">
                <button
                  className="overlay-btn preview-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    setPreviewTemplate(template);
                  }}
                >
                  🖼 Preview
                </button>
                <button
                  className="overlay-btn use-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    onSelect(template.id);
                  }}
                >
                  🪄 Use Template
                </button>
              </div>
            )}

            <div className="template-footer">
              <div className="template-info">
                <h3>{template.name}</h3>
                <span className="template-subtitle">
                  📄 {(template.file_type || 'DOCX').toUpperCase()}
                </span>
              </div>
              <div className="template-actions">
                <button
                  className={`star-btn ${favorites.includes(template.id) ? 'starred' : ''}`}
                  onClick={(e) => toggleFavorite(template.id, e)}
                  title={favorites.includes(template.id) ? 'Remove from favorites' : 'Add to favorites'}
                >
                  {favorites.includes(template.id) ? '⭐' : '☆'}
                </button>
                <button
                  className="more-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    setDeleteConfirmId(template.id);
                  }}
                  title="Delete template"
                >
                  ⋮
                </button>
              </div>
            </div>
            {selectedTemplate === template.id && (
              <div className="selected-overlay">
                <div className="checkmark">✓</div>
              </div>
            )}
          </div>
        );
        })}

        <div 
          className={`template-card add-template ${dragOver ? 'drag-over' : ''}`}
          onClick={() => setShowUploadModal(true)}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <div className="add-template-content">
            <div className="add-icon pulse">+</div>
            <h3>+ Add New Template</h3>
            <p>{dragOver ? 'Drop your .docx file here' : 'Upload or drag & drop your template'}</p>
            <span className="upload-hint">Supports .docx, .pdf, .doc</span>
          </div>
        </div>
      </div>

      {templates.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">📋</div>
          <h3>No Templates Yet</h3>
          <p>Click the + button to upload your first template</p>
        </div>
      )}

      {showUploadModal && (
        <div className="modal-overlay" onClick={() => setShowUploadModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>📤 Upload New Template</h3>
              <button className="close-btn" onClick={() => setShowUploadModal(false)}>×</button>
            </div>
            <form onSubmit={handleUpload} className="upload-form">
              <div className="form-group">
                <label>Template Name</label>
                <input
                  type="text"
                  placeholder="e.g., Company Standard Format"
                  value={templateName}
                  onChange={(e) => setTemplateName(e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <label>Template File (.pdf, .docx, .doc)</label>
                <div className="file-input-wrapper">
                  <input
                    type="file"
                    accept=".pdf,.doc,.docx"
                    onChange={(e) => setFile(e.target.files[0])}
                    required
                    id="file-input"
                  />
                  <label htmlFor="file-input" className="file-input-label">
                    {file ? file.name : 'Choose file...'}
                  </label>
                </div>
              </div>
              <div className="form-actions">
                <button type="button" className="btn-secondary" onClick={() => setShowUploadModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary" disabled={uploading}>
                  {uploading ? 'Uploading...' : 'Upload Template'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Preview Modal */}
      {previewTemplate && (
        <div className="modal-overlay preview-modal" onClick={() => setPreviewTemplate(null)}>
          <div className="modal-content preview-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>📋 {previewTemplate.name}</h3>
              <button className="close-btn" onClick={() => setPreviewTemplate(null)}>×</button>
            </div>
            <div className="preview-body">
              <div className="preview-image-container">
                <img 
                  src={`/api/templates/${previewTemplate.id}/thumbnail?t=${Date.now()}`}
                  alt={previewTemplate.name}
                  className="preview-image"
                  onError={(e) => {
                    e.currentTarget.style.display = 'none';
                  }}
                />
              </div>
              <div className="preview-details">
                <div className="detail-section">
                  <h4>Template Information</h4>
                  <p><strong>Name:</strong> {previewTemplate.name}</p>
                  <p><strong>Type:</strong> {(previewTemplate.file_type || 'DOCX').toUpperCase()}</p>
                  <p><strong>Uploaded:</strong> {new Date(previewTemplate.upload_date).toLocaleDateString()}</p>
                </div>
              </div>
            </div>
            <div className="preview-actions">
              <button className="btn-secondary" onClick={() => setPreviewTemplate(null)}>
                Close
              </button>
              <button className="btn-primary" onClick={() => {
                onSelect(previewTemplate.id);
                setPreviewTemplate(null);
              }}>
                🪄 Use This Template
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteConfirmId && (
        <div className="modal-overlay" onClick={() => !isDeleting && setDeleteConfirmId(null)}>
          <div className="modal-content delete-confirmation" onClick={(e) => e.stopPropagation()}>
            <div className="delete-icon">🗑️</div>
            <h3>Delete Template?</h3>
            <p>Are you sure you want to delete this template? This action cannot be undone.</p>
            <div className="delete-actions">
              <button 
                className="btn-secondary" 
                onClick={() => setDeleteConfirmId(null)}
                disabled={isDeleting}
              >
                Cancel
              </button>
              <button 
                className="btn-danger" 
                onClick={async () => {
                  setIsDeleting(true);
                  try {
                    await onDelete(deleteConfirmId);
                    setDeleteConfirmId(null);
                  } catch (error) {
                    console.error('Delete error:', error);
                  } finally {
                    setIsDeleting(false);
                  }
                }}
                disabled={isDeleting}
              >
                {isDeleting ? 'Deleting...' : 'Delete Template'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TemplateSelection;
