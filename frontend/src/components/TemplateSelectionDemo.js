import React, { useState, useEffect } from 'react';
import './TemplateSelectionDemo.css';

const TemplateSelectionDemo = ({ templates, selectedTemplate, onSelect, onDelete, onUpload, darkMode, onBack }) => {
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [templateName, setTemplateName] = useState('');
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [favorites, setFavorites] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [previewTemplate, setPreviewTemplate] = useState(null);
  const [carouselIndex, setCarouselIndex] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteConfirmId, setDeleteConfirmId] = useState(null);

  // Load favorites from localStorage
  useEffect(() => {
    const savedFavorites = localStorage.getItem('templateFavoritesDemo');
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
    localStorage.setItem('templateFavoritesDemo', JSON.stringify(newFavorites));
  };

  // Filter templates
  const filteredTemplates = templates.filter(template => {
    return template.name.toLowerCase().includes(searchQuery.toLowerCase());
  });

  // Get favorites
  const favoriteTemplates = filteredTemplates.filter(t => favorites.includes(t.id));

  // Get non-favorites for carousel
  const carouselTemplates = filteredTemplates.filter(t => !favorites.includes(t.id));

  // Handle carousel navigation
  const handlePrevious = () => {
    setCarouselIndex((prev) => (prev === 0 ? Math.max(0, carouselTemplates.length - 4) : Math.max(0, prev - 1)));
  };

  const handleNext = () => {
    setCarouselIndex((prev) => (prev >= carouselTemplates.length - 4 ? 0 : prev + 1));
  };

  // Get visible templates in carousel (4 at a time)
  const getVisibleTemplates = () => {
    if (carouselTemplates.length === 0) return [];
    const visible = [];
    for (let i = 0; i < Math.min(4, carouselTemplates.length); i++) {
      const index = (carouselIndex + i) % carouselTemplates.length;
      if (carouselTemplates[index]) {
        visible.push(carouselTemplates[index]);
      }
    }
    return visible;
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
    if (droppedFile && (droppedFile.name.endsWith('.docx') || droppedFile.name.endsWith('.pdf') || droppedFile.name.endsWith('.doc'))) {
      setFile(droppedFile);
      setShowUploadModal(true);
    } else {
      alert('Please drop a valid template file (.docx, .pdf, or .doc)');
    }
  };

  return (
    <div className={`template-selection-demo ${darkMode ? 'dark-mode' : ''}`}>
      {/* Demo Banner */}
      <div className="demo-banner">
        🎨 NEW DESIGN DEMO - This is the new template selection interface
      </div>

      {/* Back Button */}
      {onBack && (
        <button className="back-button-demo" onClick={onBack} title="Go back">
          <span className="back-arrow">←</span>
        </button>
      )}

      {/* Header */}
      <div className="header-section-demo">
        <h1 className="main-title-demo">RESUME FORMATTER ✨</h1>
        
        {/* Search Bar */}
        <div className="search-container-demo">
          <div className="search-bar-demo">
            <span className="search-icon-demo">🔍</span>
            <input
              type="text"
              placeholder="search to find Template"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input-demo"
            />
          </div>
        </div>
      </div>

      {/* Carousel Section */}
      <div className="carousel-section-demo">
        <button 
          className="carousel-nav-demo carousel-nav-left-demo" 
          onClick={handlePrevious}
          disabled={carouselTemplates.length <= 4}
        >
          &lt;
        </button>

        <div className="carousel-container-demo">
          <div className="carousel-track-demo">
            {getVisibleTemplates().map((template, idx) => (
              <div
                key={template.id}
                className={`carousel-card-demo ${selectedTemplate === template.id ? 'selected' : ''}`}
                onClick={() => onSelect(template.id)}
              >
                <div className="carousel-card-image-demo">
                  <img
                    src={`/api/templates/${template.id}/thumbnail?t=${Date.now()}`}
                    alt={template.name}
                    className="carousel-thumbnail-demo"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                      const fallback = e.currentTarget.nextElementSibling;
                      if (fallback && fallback instanceof HTMLElement) {
                        fallback.style.display = 'flex';
                      }
                    }}
                  />
                  <div className="template-fallback-demo" style={{display: 'none'}}>
                    <div className="doc-icon-demo">📄</div>
                    <div className="template-name-demo">{template.name}</div>
                  </div>
                </div>
                <div className="carousel-card-info-demo">
                  <h3>{template.name}</h3>
                  <p>{(template.file_type || 'DOCX').toUpperCase()} Template</p>
                </div>
                <button
                  className={`heart-btn-demo ${favorites.includes(template.id) ? 'liked' : ''}`}
                  onClick={(e) => toggleFavorite(template.id, e)}
                  title={favorites.includes(template.id) ? 'Remove from favorites' : 'Add to favorites'}
                >
                  {favorites.includes(template.id) ? '❤️' : '🤍'}
                </button>
              </div>
            ))}
          </div>
        </div>

        <button 
          className="carousel-nav-demo carousel-nav-right-demo" 
          onClick={handleNext}
          disabled={carouselTemplates.length <= 4}
        >
          &gt;
        </button>
      </div>

      {/* Add New Template Card */}
      <div className="add-template-section-demo">
        <div 
          className="add-template-card-demo"
          onClick={() => setShowUploadModal(true)}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          <div className="add-template-content-demo">
            <div className="add-icon-demo">+</div>
            <h3>Add New Template</h3>
            <p>Upload or drag & drop your template</p>
            <span className="upload-hint-demo">Supports .docx, .pdf, .doc</span>
          </div>
        </div>
      </div>

      {/* Favorites Section */}
      {favoriteTemplates.length > 0 && (
        <div className="favorites-section-demo">
          <h2 className="favorites-title-demo">Favorites ❤️</h2>
          <div className="favorites-grid-demo">
            {favoriteTemplates.map((template) => (
              <div
                key={template.id}
                className={`favorite-card-demo ${selectedTemplate === template.id ? 'selected' : ''}`}
                onClick={() => onSelect(template.id)}
              >
                <div className="favorite-card-image-demo">
                  <img
                    src={`/api/templates/${template.id}/thumbnail?t=${Date.now()}`}
                    alt={template.name}
                    className="favorite-thumbnail-demo"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                      const fallback = e.currentTarget.nextElementSibling;
                      if (fallback && fallback instanceof HTMLElement) {
                        fallback.style.display = 'flex';
                      }
                    }}
                  />
                  <div className="template-fallback-demo" style={{display: 'none'}}>
                    <div className="doc-icon-demo">📄</div>
                    <div className="template-name-demo">{template.name}</div>
                  </div>
                </div>
                <div className="favorite-card-info-demo">
                  <h3>{template.name}</h3>
                  <p>{(template.file_type || 'DOCX').toUpperCase()} Template</p>
                </div>
                <button
                  className="heart-btn-demo liked"
                  onClick={(e) => toggleFavorite(template.id, e)}
                  title="Remove from favorites"
                >
                  ❤️
                </button>
                <button
                  className="delete-btn-demo"
                  onClick={(e) => {
                    e.stopPropagation();
                    setDeleteConfirmId(template.id);
                  }}
                  title="Delete template"
                >
                  🗑️
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="modal-overlay-demo" onClick={() => setShowUploadModal(false)}>
          <div className="modal-content-demo" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header-demo">
              <h3>📤 Upload New Template</h3>
              <button className="close-btn-demo" onClick={() => setShowUploadModal(false)}>×</button>
            </div>
            <form onSubmit={handleUpload} className="upload-form-demo">
              <div className="form-group-demo">
                <label>Template Name</label>
                <input
                  type="text"
                  placeholder="e.g., Company Standard Format"
                  value={templateName}
                  onChange={(e) => setTemplateName(e.target.value)}
                  required
                />
              </div>
              <div className="form-group-demo">
                <label>Template File (.pdf, .docx, .doc)</label>
                <div className="file-input-wrapper-demo" onDragOver={handleDragOver} onDrop={handleDrop}>
                  <input
                    type="file"
                    accept=".pdf,.doc,.docx"
                    onChange={(e) => setFile(e.target.files[0])}
                    required
                    id="file-input-demo"
                  />
                  <label htmlFor="file-input-demo" className="file-input-label-demo">
                    {file ? file.name : 'Choose file or drag & drop'}
                  </label>
                </div>
              </div>
              <div className="form-actions-demo">
                <button type="button" className="btn-secondary-demo" onClick={() => setShowUploadModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary-demo" disabled={uploading}>
                  {uploading ? 'Uploading...' : 'Upload Template'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteConfirmId && (
        <div className="modal-overlay-demo" onClick={() => !isDeleting && setDeleteConfirmId(null)}>
          <div className="modal-content-demo delete-confirmation-demo" onClick={(e) => e.stopPropagation()}>
            <div className="delete-icon-demo">🗑️</div>
            <h3>Delete Template?</h3>
            <p>Are you sure you want to delete this template? This action cannot be undone.</p>
            <div className="delete-actions-demo">
              <button
                className="btn-secondary-demo"
                onClick={() => setDeleteConfirmId(null)}
                disabled={isDeleting}
              >
                Cancel
              </button>
              <button
                className="btn-danger-demo"
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

export default TemplateSelectionDemo;
