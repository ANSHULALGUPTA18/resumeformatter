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
      <div className="template-main-container">
        {/* Main Header */}
        <div className="template-header">
          <h1 className="template-main-title">Choose Resume Templates</h1>
          <p className="template-subtitle">Forem ipsum dolor sit amet, consectetur adipiscing elit.</p>
        </div>

        {/* Search and Action Bar */}
        <div className="template-controls">
          <div className="search-container">
            <span className="search-icon-new">🔍</span>
            <input
              type="text"
              placeholder="Search for Template names here"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input-new"
            />
          </div>
          <button className="new-template-btn" onClick={() => setShowUploadModal(true)}>
            <span className="plus-icon">+</span> New Template
          </button>
        </div>

        {/* Tabs */}
        <div className="template-tabs">
          <button className={`tab-btn ${favorites.length === 0 || searchQuery ? 'active' : ''}`}>
            Available Templates
          </button>
          <button className={`tab-btn ${favorites.length > 0 && !searchQuery ? 'active' : ''}`}>
            Favorites Templates
          </button>
        </div>

        {/* Templates Grid */}
        <div className="templates-grid">
          {/* Add Template Card */}
          <div className="add-template-card" onClick={() => setShowUploadModal(true)}>
          <div className="add-icon-circle">
            <svg viewBox="0 0 24 24">
              <path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" fill="none" />
            </svg>
          </div>
          <p className="add-template-text">Add New Template</p>
          <p className="add-template-hint">Click to upload</p>
        </div>

        {sortedTemplates.map((template) => {
          return (
          <div
            key={template.id}
            className={`template-card ${selectedTemplate === template.id ? 'selected' : ''}`}
            onClick={() => onSelect(template.id)}
          >
            <div className="template-preview-new">
              <img 
                src={`http://localhost:5000/api/templates/${template.id}/thumbnail?t=${Date.now()}`}
                alt={template.name}
                className="template-thumbnail"
                onError={(e) => {
                  e.currentTarget.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjI1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjI1MCIgZmlsbD0iI2YzZjRmNiIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiM5Y2EzYWYiIHRleHQtYW5jaG9yPSJtaWRkbGUiPu-8r+G0nDwvdGV4dD48L3N2Zz4=';
                }}
              />
              <button
                className={`favorite-star ${favorites.includes(template.id) ? 'active' : ''}`}
                onClick={(e) => toggleFavorite(template.id, e)}
                title={favorites.includes(template.id) ? 'Remove from favorites' : 'Add to favorites'}
              >
                <svg viewBox="0 0 24 24">
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                </svg>
              </button>
            </div>
            <div className="template-card-footer">
              <span className="template-name-badge">{template.name}</span>
              <span className="template-ref">Ref: {template.id}</span>
            </div>
          </div>
        );
        })}
        </div>
      </div>

      {/* Upload Modal */}
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
