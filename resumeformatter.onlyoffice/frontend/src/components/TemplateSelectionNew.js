import React, { useState, useEffect, useRef } from 'react';
import './TemplateSelectionNew.css';

const TemplateSelectionNew = ({ templates, selectedTemplate, onSelect, onDelete, onUpload, darkMode, onBack }) => {
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [favorites, setFavorites] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState('available');
  const scrollRef = useRef(null);

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
    if (droppedFile && (droppedFile.name.endsWith('.docx') || droppedFile.name.endsWith('.pdf') || droppedFile.name.endsWith('.doc'))) {
      setFile(droppedFile);
      setShowUploadModal(true);
    } else {
      alert('Please drop a valid template file (.docx, .pdf, or .doc)');
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
            placeholder="Search for Template names here"
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
        {currentTemplates.length === 0 ? (
          <div className="empty-state">
            <i className="far fa-heart"></i>
            <h3>{activeTab === 'favorites' ? 'No favorites yet' : 'No templates found'}</h3>
            <p>{activeTab === 'favorites' ? 'Click the star icon on any template to add it here' : 'Try adjusting your search'}</p>
          </div>
        ) : (
          <div className="scroll-wrapper">
            <button className="scroll-btn scroll-btn-left" onClick={scrollLeft} aria-label="Scroll left">
              <i className="fas fa-chevron-left"></i>
            </button>

            <div className="horizontal-scroll-container" ref={scrollRef}>
              <div className="template-row">
                {/* Add New Template Card */}
                <div className="template-card add-template-card" onClick={() => setShowUploadModal(true)}>
                  <div className="add-template-content">
                    <div className="add-icon-circle">
                      <i className="fas fa-plus"></i>
                    </div>
                    <span className="add-template-label">Add new template</span>
                  </div>
                </div>
                
                {/* Resume Template Cards */}
                {currentTemplates.map((template) => (
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
                  </div>
                ))}
              </div>
            </div>

            <button className="scroll-btn scroll-btn-right" onClick={scrollRight} aria-label="Scroll right">
              <i className="fas fa-chevron-right"></i>
            </button>
          </div>
        )}
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="modal-overlay-new" onClick={() => setShowUploadModal(false)}>
          <div className="modal-content-new" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header-new">
              <h3>Add CAI Contacts to Project Plan</h3>
              <button className="close-btn-new" onClick={() => setShowUploadModal(false)}>×</button>
            </div>
            <form onSubmit={handleUpload} className="upload-form-new">
              {/* Dropdown Section */}
              <div className="dropdown-section">
                <div className="dropdown-header">
                  <i className="fas fa-users dropdown-icon"></i>
                  <span className="dropdown-text">CAI Contacts</span>
                  <span className="dropdown-badge">5</span>
                  <i className="fas fa-chevron-down dropdown-arrow"></i>
                </div>
              </div>

              <div className="form-group-new">
                <div className="file-input-wrapper-new" onDragOver={handleDragOver} onDrop={handleDrop}>
                  <div className="upload-icon">
                    <i className="fas fa-cloud-upload-alt"></i>
                  </div>
                  <p className="upload-text">Drag and drop your resume files here (PDF, DOCX)</p>
                  <input
                    type="file"
                    accept=".pdf,.doc,.docx"
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
                  {uploading ? 'Uploading...' : 'Format'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default TemplateSelectionNew;
