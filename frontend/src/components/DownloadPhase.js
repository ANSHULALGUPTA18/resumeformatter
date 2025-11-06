import React, { useState, useRef, useEffect } from 'react';
import './DownloadPhase.css';

const DownloadPhase = ({ results, onStartOver, darkMode, toggleDarkMode }) => {
  const [selectedPreview, setSelectedPreview] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [editorConfig, setEditorConfig] = useState(null);
  const [downloadingFile, setDownloadingFile] = useState(null);
  const [headerVisible, setHeaderVisible] = useState(true);
  const [lastScrollY, setLastScrollY] = useState(0);
  const [showPopup, setShowPopup] = useState(true);
  const previewContainerRef = useRef(null);
  const editorInstanceRef = useRef(null);
  
  const handleSaveAndDownload = async (result) => {
    const filename = result.filename;
    const candidateName = result.name || 'Resume';
    const templateName = result.template_name || 'Template';
    
    setDownloadingFile(filename);
    
    try {
      console.log('💾 Saving changes...');
      
      // Wait 3 seconds for OnlyOffice to auto-save
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      console.log('📥 Downloading saved file...');
      
      // Build download URL with proper filename
      const downloadUrl = `http://localhost:5000/api/download/${filename}?name=${encodeURIComponent(candidateName)}&template=${encodeURIComponent(templateName)}`;
      
      // Fetch the file
      const response = await fetch(downloadUrl);
      
      if (!response.ok) {
        throw new Error(`Download failed: ${response.statusText}`);
      }
      
      // Get the blob
      const blob = await response.blob();
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${candidateName}_${templateName}.docx`;
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      console.log('✅ Save & Download completed');
    } catch (error) {
      console.error('❌ Save & Download error:', error);
      alert('Save & Download failed. Please try again.');
    } finally {
      // Clear downloading state
      setTimeout(() => setDownloadingFile(null), 1000);
    }
  };
  
  const handleDownload = async (result) => {
    // Just call save and download
    await handleSaveAndDownload(result);
  };
  
  const handlePreviewClick = async (result) => {
    setSelectedPreview(result);
    setPreviewLoading(true);
    setShowPopup(true); // Show popup when opening preview
  };

  const togglePopup = () => {
    setShowPopup(!showPopup);
  };

  // Handle scroll to show/hide header
  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      
      if (currentScrollY > lastScrollY && currentScrollY > 100) {
        // Scrolling down & past threshold
        setHeaderVisible(false);
      } else if (currentScrollY < lastScrollY) {
        // Scrolling up
        setHeaderVisible(true);
      }
      
      setLastScrollY(currentScrollY);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, [lastScrollY]);
  
  // Load OnlyOffice editor when preview is selected
  useEffect(() => {
    if (!selectedPreview || !previewContainerRef.current) {
      return;
    }

    const loadEditor = async () => {
      try {
        console.log('🔄 Loading editor for:', selectedPreview.filename);
        
        // Destroy existing editor if any
        if (editorInstanceRef.current) {
          try {
            console.log('🗑️ Destroying previous editor...');
            editorInstanceRef.current.destroyEditor();
            editorInstanceRef.current = null;
          } catch (e) {
            console.log('⚠️ Editor already destroyed');
          }
        }
        
        // Wait for DocsAPI to be available
        const waitForDocsAPI = () => {
          return new Promise((resolve, reject) => {
            if (window.DocsAPI) {
              console.log('✅ DocsAPI already loaded');
              resolve();
              return;
            }
            
            console.log('⏳ Waiting for DocsAPI to load...');
            let attempts = 0;
            const checkInterval = setInterval(() => {
              attempts++;
              if (window.DocsAPI) {
                console.log('✅ DocsAPI loaded!');
                clearInterval(checkInterval);
                resolve();
              } else if (attempts > 50) {
                clearInterval(checkInterval);
                reject(new Error('DocsAPI failed to load after 10 seconds'));
              }
            }, 200);
          });
        };
        
        // Wait for API
        try {
          await waitForDocsAPI();
        } catch (error) {
          console.error('❌ DocsAPI failed to load:', error);
          alert('OnlyOffice API failed to load. Please ensure OnlyOffice Docker container is running on port 8080.');
          setPreviewLoading(false);
          return;
        }
        
        // Fetch editor config
        console.log('📡 Fetching editor config...');
        const response = await fetch(`http://localhost:5000/api/onlyoffice/config/${selectedPreview.filename}`);
        
        if (!response.ok) {
          console.error('❌ Failed to fetch config:', response.status);
          alert(`Failed to fetch editor config: ${response.status}`);
          setPreviewLoading(false);
          return;
        }
        
        const config = await response.json();
        console.log('📦 Config received:', config);
        
        if (config.success) {
          console.log('✅ Config valid, initializing editor...');
          setEditorConfig(config.config);
          
          // Wait for container to be ready
          setTimeout(() => {
            if (!previewContainerRef.current) {
              console.error('❌ Container ref is null');
              setPreviewLoading(false);
              return;
            }
            
            if (!window.DocsAPI) {
              console.error('❌ DocsAPI not available');
              setPreviewLoading(false);
              return;
            }
            
            try {
              // Use a stable, fixed container ID managed by React
              const containerId = 'onlyoffice-editor';
              const mountEl = document.getElementById(containerId);
              if (!mountEl) {
                console.error('❌ Editor mount element not found');
                setPreviewLoading(false);
                return;
              }
              console.log('🚀 Creating editor instance with ID:', containerId);
              console.log('📝 Editor config:', config.config);
              
              const editor = new window.DocsAPI.DocEditor(containerId, config.config);
              editorInstanceRef.current = editor;
              setPreviewLoading(false);
              console.log('✅ Editor loaded successfully!');
            } catch (error) {
              console.error('❌ Error creating editor:', error);
              alert(`Error creating editor: ${error.message}`);
              setPreviewLoading(false);
            }
          }, 500);
        } else {
          console.error('❌ Config not successful:', config);
          alert('Failed to get valid editor configuration');
          setPreviewLoading(false);
        }
      } catch (error) {
        console.error('❌ Error loading editor:', error);
        alert(`Error loading editor: ${error.message}`);
        setPreviewLoading(false);
      }
    };

    loadEditor();
    
    // Cleanup on unmount
    return () => {
      if (editorInstanceRef.current) {
        try {
          console.log('🧹 Cleaning up editor...');
          editorInstanceRef.current.destroyEditor();
          editorInstanceRef.current = null;
        } catch (e) {
          console.log('⚠️ Cleanup: Editor already destroyed');
        }
      }
    };
  }, [selectedPreview]);


  const handleDownloadAll = () => {
    results.forEach((result, index) => {
      setTimeout(() => {
        handleDownload(result);
      }, index * 500); // Stagger downloads by 500ms
    });
  };

  return (
    <div className="download-phase-v2">
      {/* Ultra-Compact Status Bar */}
      <div className={`status-bar ${!headerVisible ? 'hidden' : ''}`}>
        <div className="status-left">
          <div className="app-branding">
            <span className="app-icon">✨</span>
            <span className="app-name">Resume Formatter Pro</span>
          </div>
          <div className="status-divider"></div>
          <div className="status-badge success">
            <span className="badge-icon">✓</span>
            <span className="badge-text">Complete</span>
          </div>
          <div className="status-info">
            <span className="info-count">{results.length}</span>
            <span className="info-label">resume{results.length !== 1 ? 's' : ''} formatted</span>
          </div>
        </div>
        <div className="status-actions">
          {results.length > 1 && (
            <button className="status-btn" onClick={handleDownloadAll} title="Download All">
              <span className="btn-icon">⬇️</span>
              <span className="btn-label">All</span>
            </button>
          )}
          <button 
            className="status-btn secondary" 
            onClick={toggleDarkMode} 
            title={darkMode ? 'Light Mode' : 'Dark Mode'}
          >
            <span className="btn-icon">{darkMode ? '☀️' : '🌙'}</span>
            <span className="btn-label">{darkMode ? 'Light' : 'Dark'}</span>
          </button>
        </div>
      </div>

      {/* Horizontal Tab Bar for File Selection with Format More Button */}
      <div className={`file-tabs-bar ${!headerVisible ? 'hidden' : ''}`}>
        <div className="tabs-hint-banner">
          <span className="hint-icon">👇</span>
          <span className="hint-text">Click any resume below to preview and edit</span>
        </div>
        <div className="tabs-row-wrapper">
          <div className="tabs-container">
            {results.map((result, index) => (
            <div
              key={index}
              className={`file-tab ${selectedPreview?.filename === result.filename ? 'active' : ''} ${!selectedPreview ? 'pulse-animation' : ''}`}
              onClick={() => handlePreviewClick(result)}
              title="Click to preview and edit"
            >
              <div className="tab-icon-wrapper">
                <div className="tab-icon">📄</div>
                <div className="click-indicator">👆</div>
              </div>
              <div className="tab-content">
                <div className="tab-name-wrapper">
                  <div className="tab-name">{result.name || `Resume ${index + 1}`}</div>
                  <div className="tab-subtitle">Click to edit</div>
                </div>
                <div className="tab-badge">DOCX</div>
              </div>
              <div className="tab-actions">
                <button
                  className="tab-download"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDownload(result);
                  }}
                  title="Download"
                >
                  ⬇️
                </button>
              </div>
            </div>
          ))}
          </div>
          
          {/* Format More Button - Fixed on Right */}
          <button className="format-more-btn-compact" onClick={onStartOver} title="Format More Resumes">
            <span className="format-more-icon-compact">📝</span>
            <span className="format-more-text-compact">Format More</span>
          </button>
        </div>
      </div>

      {/* Full-Screen Editor */}
      <div className="editor-workspace-v2">
        {!selectedPreview ? (
          <div className="welcome-screen">
            <div className="welcome-content">
              <div className="welcome-icon">🎉</div>
              <h1 className="welcome-title">Your Resumes Are Ready!</h1>
              <p className="welcome-subtitle">Select a resume from the tabs above to start editing</p>
              
              <div className="welcome-features">
                <div className="feature-card">
                  <div className="feature-card-icon">✏️</div>
                  <h3>Full Editing Power</h3>
                  <p>Change fonts, colors, and formatting</p>
                </div>
                <div className="feature-card">
                  <div className="feature-card-icon">💾</div>
                  <h3>Auto-Save</h3>
                  <p>Your changes save automatically</p>
                </div>
                <div className="feature-card">
                  <div className="feature-card-icon">⬇️</div>
                  <h3>Quick Download</h3>
                  <p>Download anytime with one click</p>
                </div>
              </div>

              <div className="welcome-action">
                <button 
                  className="welcome-btn"
                  onClick={() => handlePreviewClick(results[0])}
                >
                  <span>🚀</span> Start Editing First Resume
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="editor-view">
            {/* Floating Popup with Download */}
            {showPopup && (
              <div className="floating-popup">
                <div className="popup-content">
                  <div 
                    className="popup-info"
                    onClick={togglePopup}
                    style={{ cursor: 'pointer' }}
                    title="Click to toggle popup"
                  >
                    <span className="popup-icon">✏️</span>
                    <span className="popup-name">{selectedPreview.name || 'Resume'}</span>
                    <span className="live-badge">● Live</span>
                  </div>
                  <div className="popup-actions">
                    <button 
                      className="popup-save-btn"
                      onClick={() => handleSaveAndDownload(selectedPreview)}
                      disabled={downloadingFile === selectedPreview.filename}
                      title="Save changes and download"
                    >
                      {downloadingFile === selectedPreview.filename ? '⏳ Saving...' : '💾 Save & Download'}
                    </button>
                    <button 
                      className="popup-close-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        setShowPopup(false);
                      }}
                      title="Close popup (not preview)"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Editor Container */}
            <div className="editor-frame">
              {previewLoading && (
                <div className="editor-loader">
                  <div className="loader-spinner"></div>
                  <p className="loader-text">Loading editor...</p>
                </div>
              )}
              <div 
                className="onlyoffice-editor-container"
                style={{ 
                  display: previewLoading ? 'none' : 'block',
                  width: '100%',
                  height: 'calc(100vh - 150px)',
                  minHeight: 'calc(100vh - 150px)'
                }}
              >
                {/* Stable mount node for OnlyOffice. Do NOT change its id dynamically. */}
                <div id="onlyoffice-editor" ref={previewContainerRef} style={{ height: '100%', width: '100%' }} />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DownloadPhase;
